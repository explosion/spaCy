from thinc.api import chain, clone, concatenate, with_array, uniqued
from thinc.api import Model, noop, with_padded, Maxout, expand_window
from thinc.api import HashEmbed, StaticVectors, PyTorchLSTM
from thinc.api import residual, LayerNorm, FeatureExtractor, Mish

from ... import util
from ...util import registry
from ...ml import _character_embed
from ...pipeline.tok2vec import Tok2VecListener
from ...attrs import ID, ORTH, NORM, PREFIX, SUFFIX, SHAPE


@registry.architectures.register("spacy.Tok2VecTensors.v1")
def tok2vec_tensors_v1(width):
    tok2vec = Tok2VecListener("tok2vec", width=width)
    return tok2vec


@registry.architectures.register("spacy.VocabVectors.v1")
def get_vocab_vectors(name):
    nlp = util.load_model(name)
    return nlp.vocab.vectors


@registry.architectures.register("spacy.Tok2Vec.v1")
def Tok2Vec(extract, embed, encode):
    field_size = 0
    if encode.attrs.get("receptive_field", None):
        field_size = encode.attrs["receptive_field"]
    with Model.define_operators({">>": chain, "|": concatenate}):
        tok2vec = extract >> with_array(embed >> encode, pad=field_size)
    tok2vec.set_dim("nO", encode.get_dim("nO"))
    tok2vec.set_ref("embed", embed)
    tok2vec.set_ref("encode", encode)
    return tok2vec


@registry.architectures.register("spacy.Doc2Feats.v1")
def Doc2Feats(columns):
    return FeatureExtractor(columns)


@registry.architectures.register("spacy.HashEmbedCNN.v1")
def hash_embed_cnn(
    pretrained_vectors,
    width,
    depth,
    embed_size,
    maxout_pieces,
    window_size,
    subword_features,
    dropout,
):
    # Does not use character embeddings: set to False by default
    return build_Tok2Vec_model(
        width=width,
        embed_size=embed_size,
        pretrained_vectors=pretrained_vectors,
        conv_depth=depth,
        bilstm_depth=0,
        maxout_pieces=maxout_pieces,
        window_size=window_size,
        subword_features=subword_features,
        char_embed=False,
        nM=0,
        nC=0,
        dropout=dropout,
    )


@registry.architectures.register("spacy.HashCharEmbedCNN.v1")
def hash_charembed_cnn(
    pretrained_vectors,
    width,
    depth,
    embed_size,
    maxout_pieces,
    window_size,
    nM,
    nC,
    dropout,
):
    # Allows using character embeddings by setting nC, nM and char_embed=True
    return build_Tok2Vec_model(
        width=width,
        embed_size=embed_size,
        pretrained_vectors=pretrained_vectors,
        conv_depth=depth,
        bilstm_depth=0,
        maxout_pieces=maxout_pieces,
        window_size=window_size,
        subword_features=False,
        char_embed=True,
        nM=nM,
        nC=nC,
        dropout=dropout,
    )


@registry.architectures.register("spacy.HashEmbedBiLSTM.v1")
def hash_embed_bilstm_v1(
    pretrained_vectors,
    width,
    depth,
    embed_size,
    subword_features,
    maxout_pieces,
    dropout,
):
    # Does not use character embeddings: set to False by default
    return build_Tok2Vec_model(
        width=width,
        embed_size=embed_size,
        pretrained_vectors=pretrained_vectors,
        bilstm_depth=depth,
        conv_depth=0,
        maxout_pieces=maxout_pieces,
        window_size=1,
        subword_features=subword_features,
        char_embed=False,
        nM=0,
        nC=0,
        dropout=dropout,
    )


@registry.architectures.register("spacy.HashCharEmbedBiLSTM.v1")
def hash_char_embed_bilstm_v1(
    pretrained_vectors, width, depth, embed_size, maxout_pieces, nM, nC, dropout
):
    # Allows using character embeddings by setting nC, nM and char_embed=True
    return build_Tok2Vec_model(
        width=width,
        embed_size=embed_size,
        pretrained_vectors=pretrained_vectors,
        bilstm_depth=depth,
        conv_depth=0,
        maxout_pieces=maxout_pieces,
        window_size=1,
        subword_features=False,
        char_embed=True,
        nM=nM,
        nC=nC,
        dropout=dropout,
    )


@registry.architectures.register("spacy.LayerNormalizedMaxout.v1")
def LayerNormalizedMaxout(width, maxout_pieces):
    return Maxout(nO=width, nP=maxout_pieces, dropout=0.0, normalize=True)


@registry.architectures.register("spacy.MultiHashEmbed.v1")
def MultiHashEmbed(
    columns, width, rows, use_subwords, pretrained_vectors, mix, dropout
):
    norm = HashEmbed(nO=width, nV=rows, column=columns.index("NORM"), dropout=dropout, seed=6)
    if use_subwords:
        prefix = HashEmbed(
            nO=width, nV=rows // 2, column=columns.index("PREFIX"), dropout=dropout, seed=7
        )
        suffix = HashEmbed(
            nO=width, nV=rows // 2, column=columns.index("SUFFIX"), dropout=dropout, seed=8
        )
        shape = HashEmbed(
            nO=width, nV=rows // 2, column=columns.index("SHAPE"), dropout=dropout, seed=9
        )

    if pretrained_vectors:
        glove = StaticVectors(
            vectors=pretrained_vectors.data,
            nO=width,
            column=columns.index(ID),
            dropout=dropout,
        )

    with Model.define_operators({">>": chain, "|": concatenate}):
        if not use_subwords and not pretrained_vectors:
            embed_layer = norm
        else:
            if use_subwords and pretrained_vectors:
                concat_columns = glove | norm | prefix | suffix | shape
            elif use_subwords:
                concat_columns = norm | prefix | suffix | shape
            else:
                concat_columns = glove | norm

            embed_layer = uniqued(concat_columns >> mix, column=columns.index("ORTH"))

    return embed_layer


@registry.architectures.register("spacy.CharacterEmbed.v1")
def CharacterEmbed(columns, width, rows, nM, nC, features, dropout):
    norm = HashEmbed(nO=width, nV=rows, column=columns.index("NORM"), dropout=dropout, seed=5)
    chr_embed = _character_embed.CharacterEmbed(nM=nM, nC=nC)
    with Model.define_operators({">>": chain, "|": concatenate}):
        embed_layer = chr_embed | features >> with_array(norm)
    embed_layer.set_dim("nO", nM * nC + width)
    return embed_layer


@registry.architectures.register("spacy.MaxoutWindowEncoder.v1")
def MaxoutWindowEncoder(width, window_size, maxout_pieces, depth):
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
def MishWindowEncoder(width, window_size, depth):
    cnn = chain(
        expand_window(window_size=window_size),
        Mish(nO=width, nI=width * ((window_size * 2) + 1)),
        LayerNorm(width),
    )
    model = clone(residual(cnn), depth)
    model.set_dim("nO", width)
    return model


@registry.architectures.register("spacy.TorchBiLSTMEncoder.v1")
def TorchBiLSTMEncoder(width, depth):
    import torch.nn

    # TODO FIX
    from thinc.api import PyTorchRNNWrapper

    if depth == 0:
        return noop()
    return with_padded(
        PyTorchRNNWrapper(torch.nn.LSTM(width, width // 2, depth, bidirectional=True))
    )


def build_Tok2Vec_model(
    width,
    embed_size,
    pretrained_vectors,
    window_size,
    maxout_pieces,
    subword_features,
    char_embed,
    nM,
    nC,
    conv_depth,
    bilstm_depth,
    dropout,
) -> Model:
    if char_embed:
        subword_features = False
    cols = [ID, NORM, PREFIX, SUFFIX, SHAPE, ORTH]
    with Model.define_operators({">>": chain, "|": concatenate, "**": clone}):
        norm = HashEmbed(
            nO=width, nV=embed_size, column=cols.index(NORM), dropout=None,
            seed=0
        )
        if subword_features:
            prefix = HashEmbed(
                nO=width, nV=embed_size // 2, column=cols.index(PREFIX), dropout=None,
                seed=1
            )
            suffix = HashEmbed(
                nO=width, nV=embed_size // 2, column=cols.index(SUFFIX), dropout=None,
                seed=2
            )
            shape = HashEmbed(
                nO=width, nV=embed_size // 2, column=cols.index(SHAPE), dropout=None,
                seed=3
            )
        else:
            prefix, suffix, shape = (None, None, None)
        if pretrained_vectors is not None:
            glove = StaticVectors(
                vectors=pretrained_vectors.data,
                nO=width,
                column=cols.index(ID),
                dropout=dropout,
            )

            if subword_features:
                columns = 5
                embed = uniqued(
                    (glove | norm | prefix | suffix | shape)
                    >> Maxout(
                        nO=width,
                        nI=width * columns,
                        nP=3,
                        dropout=0.0,
                        normalize=True,
                    ),
                    column=cols.index(ORTH),
                )
            else:
                columns = 2
                embed = uniqued(
                    (glove | norm)
                    >> Maxout(
                        nO=width,
                        nI=width * columns,
                        nP=3,
                        dropout=0.0,
                        normalize=True,
                    ),
                    column=cols.index(ORTH),
                )
        elif subword_features:
            columns = 4
            embed = uniqued(
                concatenate(norm, prefix, suffix, shape)
                >> Maxout(
                    nO=width,
                    nI=width * columns,
                    nP=3,
                    dropout=0.0,
                    normalize=True,
                ),
                column=cols.index(ORTH),
            )
        elif char_embed:
            embed = _character_embed.CharacterEmbed(nM=nM, nC=nC) | FeatureExtractor(
                cols
            ) >> with_array(norm)
            reduce_dimensions = Maxout(
                nO=width,
                nI=nM * nC + width,
                nP=3,
                dropout=0.0,
                normalize=True,
            )
        else:
            embed = norm

        convolution = residual(
            expand_window(window_size=window_size)
            >> Maxout(
                nO=width,
                nI=width * ((window_size * 2) + 1),
                nP=maxout_pieces,
                dropout=0.0,
                normalize=True,
            )
        )
        if char_embed:
            tok2vec = embed >> with_array(
                reduce_dimensions >> convolution ** conv_depth, pad=conv_depth
            )
        else:
            tok2vec = FeatureExtractor(cols) >> with_array(
                embed >> convolution ** conv_depth, pad=conv_depth
            )

        if bilstm_depth >= 1:
            tok2vec = tok2vec >> PyTorchLSTM(
                nO=width, nI=width, depth=bilstm_depth, bi=True
            )
        if tok2vec.has_dim("nO") is not False:
            tok2vec.set_dim("nO", width)
        tok2vec.set_ref("embed", embed)
    return tok2vec
