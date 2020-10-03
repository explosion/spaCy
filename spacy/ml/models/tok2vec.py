from typing import Optional, List, Union
from thinc.types import Floats2d
from thinc.api import chain, clone, concatenate, with_array, with_padded
from thinc.api import Model, noop, list2ragged, ragged2list, HashEmbed
from thinc.api import expand_window, residual, Maxout, Mish, PyTorchLSTM

from ...tokens import Doc
from ...util import registry
from ...ml import _character_embed
from ..staticvectors import StaticVectors
from ..featureextractor import FeatureExtractor
from ...pipeline.tok2vec import Tok2VecListener
from ...attrs import ORTH, LOWER, PREFIX, SUFFIX, SHAPE, intify_attr


@registry.architectures.register("spacy.Tok2VecListener.v1")
def tok2vec_listener_v1(width: int, upstream: str = "*"):
    tok2vec = Tok2VecListener(upstream_name=upstream, width=width)
    return tok2vec


@registry.architectures.register("spacy.HashEmbedCNN.v1")
def build_hash_embed_cnn_tok2vec(
    *,
    width: int,
    depth: int,
    embed_size: int,
    window_size: int,
    maxout_pieces: int,
    subword_features: bool,
    pretrained_vectors: Optional[bool]
) -> Model[List[Doc], List[Floats2d]]:
    """Build spaCy's 'standard' tok2vec layer, which uses hash embedding
    with subword features and a CNN with layer-normalized maxout.

    width (int): The width of the input and output. These are required to be the
        same, so that residual connections can be used. Recommended values are
        96, 128 or 300.
    depth (int): The number of convolutional layers to use. Recommended values
        are between 2 and 8.
    window_size (int): The number of tokens on either side to concatenate during
        the convolutions. The receptive field of the CNN will be
        depth * (window_size * 2 + 1), so a 4-layer network with window_size of
        2 will be sensitive to 17 words at a time. Recommended value is 1.
    embed_size (int): The number of rows in the hash embedding tables. This can
        be surprisingly small, due to the use of the hash embeddings. Recommended
        values are between 2000 and 10000.
    maxout_pieces (int): The number of pieces to use in the maxout non-linearity.
        If 1, the Mish non-linearity is used instead. Recommended values are 1-3.
    subword_features (bool): Whether to also embed subword features, specifically
        the prefix, suffix and word shape. This is recommended for alphabetic
        languages like English, but not if single-character tokens are used for
        a language such as Chinese.
    pretrained_vectors (bool): Whether to also use static vectors.
    """
    return build_Tok2Vec_model(
        embed=MultiHashEmbed(
            width=width,
            rows=embed_size,
            also_embed_subwords=subword_features,
            also_use_static_vectors=bool(pretrained_vectors),
        ),
        encode=MaxoutWindowEncoder(
            width=width,
            depth=depth,
            window_size=window_size,
            maxout_pieces=maxout_pieces,
        ),
    )


@registry.architectures.register("spacy.Tok2Vec.v1")
def build_Tok2Vec_model(
    embed: Model[List[Doc], List[Floats2d]],
    encode: Model[List[Floats2d], List[Floats2d]],
) -> Model[List[Doc], List[Floats2d]]:
    """Construct a tok2vec model out of embedding and encoding subnetworks.
    See https://explosion.ai/blog/deep-learning-formula-nlp

    embed (Model[List[Doc], List[Floats2d]]): Embed tokens into context-independent
        word vector representations.
    encode (Model[List[Floats2d], List[Floats2d]]): Encode context into the
        embeddings, using an architecture such as a CNN, BiLSTM or transformer.
    """
    receptive_field = encode.attrs.get("receptive_field", 0)
    tok2vec = chain(embed, with_array(encode, pad=receptive_field))
    tok2vec.set_dim("nO", encode.get_dim("nO"))
    tok2vec.set_ref("embed", embed)
    tok2vec.set_ref("encode", encode)
    return tok2vec


@registry.architectures.register("spacy.MultiHashEmbed.v1")
def MultiHashEmbed(
    width: int, rows: int, also_embed_subwords: bool, also_use_static_vectors: bool
) -> Model[List[Doc], List[Floats2d]]:
    """Construct an embedding layer that separately embeds a number of lexical
    attributes using hash embedding, concatenates the results, and passes it
    through a feed-forward subnetwork to build a mixed representations.

    The features used are the LOWER, PREFIX, SUFFIX and SHAPE, which can have
    varying definitions depending on the Vocab of the Doc object passed in.
    Vectors from pretrained static vectors can also be incorporated into the
    concatenated representation.

    width (int): The output width. Also used as the width of the embedding tables.
        Recommended values are between 64 and 300.
    rows (int): The number of rows for the embedding tables. Can be low, due
        to the hashing trick. Embeddings for prefix, suffix and word shape
        use half as many rows. Recommended values are between 2000 and 10000.
    also_embed_subwords (bool): Whether to use the PREFIX, SUFFIX and SHAPE
        features in the embeddings. If not using these, you may need more
        rows in your hash embeddings, as there will be increased chance of
        collisions.
    also_use_static_vectors (bool): Whether to also use static word vectors.
        Requires a vectors table to be loaded in the Doc objects' vocab.
    """
    cols = [LOWER, PREFIX, SUFFIX, SHAPE, ORTH]
    seed = 7

    def make_hash_embed(feature):
        nonlocal seed
        seed += 1
        return HashEmbed(
            width,
            rows if feature == LOWER else rows // 2,
            column=cols.index(feature),
            seed=seed,
            dropout=0.0,
        )

    if also_embed_subwords:
        embeddings = [
            make_hash_embed(LOWER),
            make_hash_embed(PREFIX),
            make_hash_embed(SUFFIX),
            make_hash_embed(SHAPE),
        ]
    else:
        embeddings = [make_hash_embed(LOWER)]
    concat_size = width * (len(embeddings) + also_use_static_vectors)
    if also_use_static_vectors:
        model = chain(
            concatenate(
                chain(
                    FeatureExtractor(cols),
                    list2ragged(),
                    with_array(concatenate(*embeddings)),
                ),
                StaticVectors(width, dropout=0.0),
            ),
            with_array(Maxout(width, concat_size, nP=3, dropout=0.0, normalize=True)),
            ragged2list(),
        )
    else:
        model = chain(
            FeatureExtractor(cols),
            list2ragged(),
            with_array(concatenate(*embeddings)),
            with_array(Maxout(width, concat_size, nP=3, dropout=0.0, normalize=True)),
            ragged2list(),
        )
    return model


@registry.architectures.register("spacy.CharacterEmbed.v1")
def CharacterEmbed(
    width: int, rows: int, nM: int, nC: int, also_use_static_vectors: bool,
    feature: Union[int, str]="LOWER"
) -> Model[List[Doc], List[Floats2d]]:
    """Construct an embedded representation based on character embeddings, using
    a feed-forward network. A fixed number of UTF-8 byte characters are used for
    each word, taken from the beginning and end of the word equally. Padding is
    used in the centre for words that are too short.

    For instance, let's say nC=4, and the word is "jumping". The characters
    used will be jung (two from the start, two from the end). If we had nC=8,
    the characters would be "jumpping": 4 from the start, 4 from the end. This
    ensures that the final character is always in the last position, instead
    of being in an arbitrary position depending on the word length.

    The characters are embedded in a embedding table with a given number of rows,
    and the vectors concatenated. A hash-embedded vector of the LOWER of the word is
    also concatenated on, and the result is then passed through a feed-forward
    network to construct a single vector to represent the information.

    feature (int or str): An attribute to embed, to concatenate with the characters.
    width (int): The width of the output vector and the feature embedding.
    rows (int): The number of rows in the LOWER hash embedding table.
    nM (int): The dimensionality of the character embeddings. Recommended values
        are between 16 and 64.
    nC (int): The number of UTF-8 bytes to embed per word. Recommended values
        are between 3 and 8, although it may depend on the length of words in the
        language.
    also_use_static_vectors (bool): Whether to also use static word vectors.
        Requires a vectors table to be loaded in the Doc objects' vocab.
    """
    feature = intify_attr(feature)
    if feature is None:
        raise ValueError("Invalid feature: Must be a token attribute.")
    if also_use_static_vectors:
        model = chain(
            concatenate(
                chain(_character_embed.CharacterEmbed(nM=nM, nC=nC), list2ragged()),
                chain(
                    FeatureExtractor([feature]),
                    list2ragged(),
                    with_array(HashEmbed(nO=width, nV=rows, column=0, seed=5)),
                ),
                StaticVectors(width, dropout=0.0),
            ),
            with_array(
                Maxout(width, nM * nC + (2 * width), nP=3, normalize=True, dropout=0.0)
            ),
            ragged2list(),
        )
    else:
        model = chain(
            concatenate(
                chain(_character_embed.CharacterEmbed(nM=nM, nC=nC), list2ragged()),
                chain(
                    FeatureExtractor([feature]),
                    list2ragged(),
                    with_array(HashEmbed(nO=width, nV=rows, column=0, seed=5)),
                ),
            ),
            with_array(
                Maxout(width, nM * nC + width, nP=3, normalize=True, dropout=0.0)
            ),
            ragged2list(),
        )
    return model


@registry.architectures.register("spacy.MaxoutWindowEncoder.v1")
def MaxoutWindowEncoder(
    width: int, window_size: int, maxout_pieces: int, depth: int
) -> Model[List[Floats2d], List[Floats2d]]:
    """Encode context using convolutions with maxout activation, layer
    normalization and residual connections.

    width (int): The input and output width. These are required to be the same,
        to allow residual connections. This value will be determined by the
        width of the inputs. Recommended values are between 64 and 300.
    window_size (int): The number of words to concatenate around each token
        to construct the convolution. Recommended value is 1.
    maxout_pieces (int): The number of maxout pieces to use. Recommended
        values are 2 or 3.
    depth (int): The number of convolutional layers. Recommended value is 4.
    """
    cnn = chain(
        expand_window(window_size=window_size),
        Maxout(
            nO=width,
            nI=width * ((window_size * 2) + 1),
            nP=maxout_pieces,
            dropout=0.0,
            normalize=True,
        ),
    )
    model = clone(residual(cnn), depth)
    model.set_dim("nO", width)
    model.attrs["receptive_field"] = window_size * depth
    return model


@registry.architectures.register("spacy.MishWindowEncoder.v1")
def MishWindowEncoder(
    width: int, window_size: int, depth: int
) -> Model[List[Floats2d], List[Floats2d]]:
    """Encode context using convolutions with mish activation, layer
    normalization and residual connections.

    width (int): The input and output width. These are required to be the same,
        to allow residual connections. This value will be determined by the
        width of the inputs. Recommended values are between 64 and 300.
    window_size (int): The number of words to concatenate around each token
        to construct the convolution. Recommended value is 1.
    depth (int): The number of convolutional layers. Recommended value is 4.
    """
    cnn = chain(
        expand_window(window_size=window_size),
        Mish(nO=width, nI=width * ((window_size * 2) + 1), dropout=0.0, normalize=True),
    )
    model = clone(residual(cnn), depth)
    model.set_dim("nO", width)
    return model


@registry.architectures.register("spacy.TorchBiLSTMEncoder.v1")
def BiLSTMEncoder(
    width: int, depth: int, dropout: float
) -> Model[List[Floats2d], List[Floats2d]]:
    """Encode context using bidirectonal LSTM layers. Requires PyTorch.

    width (int): The input and output width. These are required to be the same,
        to allow residual connections. This value will be determined by the
        width of the inputs. Recommended values are between 64 and 300.
    window_size (int): The number of words to concatenate around each token
        to construct the convolution. Recommended value is 1.
    depth (int): The number of convolutional layers. Recommended value is 4.
    """
    if depth == 0:
        return noop()
    return with_padded(PyTorchLSTM(width, width, bi=True, depth=depth, dropout=dropout))
