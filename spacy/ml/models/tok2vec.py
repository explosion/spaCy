from typing import List, Optional, Union, cast

from thinc.api import (
    HashEmbed,
    Maxout,
    Mish,
    Model,
    PyTorchLSTM,
    chain,
    clone,
    concatenate,
    expand_window,
    list2ragged,
    noop,
    ragged2list,
    residual,
    with_array,
    with_padded,
)
from thinc.types import Floats2d, Ints1d, Ints2d, Ragged

from ...attrs import intify_attr
from ...errors import Errors
from ...ml import _character_embed
from ...pipeline.tok2vec import Tok2VecListener
from ...tokens import Doc
from ...util import registry
from ..featureextractor import FeatureExtractor
from ..staticvectors import StaticVectors


@registry.architectures("spacy.Tok2VecListener.v1")
def tok2vec_listener_v1(width: int, upstream: str = "*"):
    tok2vec = Tok2VecListener(upstream_name=upstream, width=width)
    return tok2vec


def get_tok2vec_width(model: Model):
    nO = None
    if model.has_ref("tok2vec"):
        tok2vec = model.get_ref("tok2vec")
        if tok2vec.has_dim("nO"):
            nO = tok2vec.get_dim("nO")
        elif tok2vec.has_ref("listener"):
            nO = tok2vec.get_ref("listener").get_dim("nO")
    return nO


@registry.architectures("spacy.HashEmbedCNN.v2")
def build_hash_embed_cnn_tok2vec(
    *,
    width: int,
    depth: int,
    embed_size: int,
    window_size: int,
    maxout_pieces: int,
    subword_features: bool,
    pretrained_vectors: Optional[bool],
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
        2 will be sensitive to 20 words at a time. Recommended value is 1.
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
    if subword_features:
        attrs = ["NORM", "PREFIX", "SUFFIX", "SHAPE"]
        row_sizes = [embed_size, embed_size // 2, embed_size // 2, embed_size // 2]
    else:
        attrs = ["NORM"]
        row_sizes = [embed_size]
    return build_Tok2Vec_model(
        embed=MultiHashEmbed(
            width=width,
            rows=row_sizes,
            attrs=attrs,
            include_static_vectors=bool(pretrained_vectors),
        ),
        encode=MaxoutWindowEncoder(
            width=width,
            depth=depth,
            window_size=window_size,
            maxout_pieces=maxout_pieces,
        ),
    )


@registry.architectures("spacy.Tok2Vec.v2")
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
    tok2vec = chain(embed, encode)
    if encode.has_dim("nO"):
        tok2vec.set_dim("nO", encode.get_dim("nO"))
    tok2vec.set_ref("embed", embed)
    tok2vec.set_ref("encode", encode)
    return tok2vec


@registry.architectures("spacy.MultiHashEmbed.v2")
def MultiHashEmbed(
    width: int,
    attrs: List[Union[str, int]],
    rows: List[int],
    include_static_vectors: bool,
) -> Model[List[Doc], List[Floats2d]]:
    """Construct an embedding layer that separately embeds a number of lexical
    attributes using hash embedding, concatenates the results, and passes it
    through a feed-forward subnetwork to build a mixed representation.

    The features used can be configured with the 'attrs' argument. The suggested
    attributes are NORM, PREFIX, SUFFIX and SHAPE. This lets the model take into
    account some subword information, without constructing a fully character-based
    representation. If pretrained vectors are available, they can be included in
    the representation as well, with the vectors table kept static
    (i.e. it's not updated).

    The `width` parameter specifies the output width of the layer and the widths
    of all embedding tables. If static vectors are included, a learned linear
    layer is used to map the vectors to the specified width before concatenating
    it with the other embedding outputs. A single Maxout layer is then used to
    reduce the concatenated vectors to the final width.

    The `rows` parameter controls the number of rows used by the `HashEmbed`
    tables. The HashEmbed layer needs surprisingly few rows, due to its use of
    the hashing trick. Generally between 2000 and 10000 rows is sufficient,
    even for very large vocabularies. A number of rows must be specified for each
    table, so the `rows` list must be of the same length as the `attrs` parameter.

    width (int): The output width. Also used as the width of the embedding tables.
        Recommended values are between 64 and 300.
    attrs (list of attr IDs): The token attributes to embed. A separate
        embedding table will be constructed for each attribute.
    rows (List[int]): The number of rows in the embedding tables. Must have the
        same length as attrs.
    include_static_vectors (bool): Whether to also use static word vectors.
        Requires a vectors table to be loaded in the Doc objects' vocab.
    """
    if len(rows) != len(attrs):
        raise ValueError(f"Mismatched lengths: {len(rows)} vs {len(attrs)}")
    seed = 7

    def make_hash_embed(index):
        nonlocal seed
        seed += 1
        return HashEmbed(width, rows[index], column=index, seed=seed, dropout=0.0)

    embeddings = [make_hash_embed(i) for i in range(len(attrs))]
    concat_size = width * (len(embeddings) + include_static_vectors)
    max_out: Model[Ragged, Ragged] = with_array(
        Maxout(width, concat_size, nP=3, dropout=0.0, normalize=True)
    )
    if include_static_vectors:
        feature_extractor: Model[List[Doc], Ragged] = chain(
            FeatureExtractor(attrs),
            cast(Model[List[Ints2d], Ragged], list2ragged()),
            with_array(concatenate(*embeddings)),
        )
        model = chain(
            concatenate(
                feature_extractor,
                StaticVectors(width, dropout=0.0),
            ),
            max_out,
            ragged2list(),
        )
    else:
        model = chain(
            FeatureExtractor(list(attrs)),
            cast(Model[List[Ints2d], Ragged], list2ragged()),
            with_array(concatenate(*embeddings)),
            max_out,
            ragged2list(),
        )
    return model


@registry.architectures("spacy.CharacterEmbed.v2")
def CharacterEmbed(
    width: int,
    rows: int,
    nM: int,
    nC: int,
    include_static_vectors: bool,
    feature: Union[int, str] = "LOWER",
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
    include_static_vectors (bool): Whether to also use static word vectors.
        Requires a vectors table to be loaded in the Doc objects' vocab.
    """
    feature = intify_attr(feature)
    if feature is None:
        raise ValueError(Errors.E911.format(feat=feature))
    char_embed = chain(
        _character_embed.CharacterEmbed(nM=nM, nC=nC),
        cast(Model[List[Floats2d], Ragged], list2ragged()),
    )
    feature_extractor: Model[List[Doc], Ragged] = chain(
        FeatureExtractor([feature]),
        cast(Model[List[Ints2d], Ragged], list2ragged()),
        with_array(HashEmbed(nO=width, nV=rows, column=0, seed=5)),  # type: ignore[misc]
    )
    max_out: Model[Ragged, Ragged]
    if include_static_vectors:
        max_out = with_array(
            Maxout(width, nM * nC + (2 * width), nP=3, normalize=True, dropout=0.0)
        )
        model = chain(
            concatenate(
                char_embed,
                feature_extractor,
                StaticVectors(width, dropout=0.0),
            ),
            max_out,
            ragged2list(),
        )
    else:
        max_out = with_array(
            Maxout(width, nM * nC + width, nP=3, normalize=True, dropout=0.0)
        )
        model = chain(
            concatenate(
                char_embed,
                feature_extractor,
            ),
            max_out,
            ragged2list(),
        )
    return model


@registry.architectures("spacy.MaxoutWindowEncoder.v2")
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
    receptive_field = window_size * depth
    return with_array(model, pad=receptive_field)


@registry.architectures("spacy.MishWindowEncoder.v2")
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
    return with_array(model)


@registry.architectures("spacy.TorchBiLSTMEncoder.v1")
def BiLSTMEncoder(
    width: int, depth: int, dropout: float
) -> Model[List[Floats2d], List[Floats2d]]:
    """Encode context using bidirectonal LSTM layers. Requires PyTorch.

    width (int): The input and output width. These are required to be the same,
        to allow residual connections. This value will be determined by the
        width of the inputs. Recommended values are between 64 and 300.
    depth (int): The number of recurrent layers.
    dropout (float): Creates a Dropout layer on the outputs of each LSTM layer
        except the last layer. Set to 0 to disable this functionality.
    """
    if depth == 0:
        return noop()
    return with_padded(PyTorchLSTM(width, width, bi=True, depth=depth, dropout=dropout))
