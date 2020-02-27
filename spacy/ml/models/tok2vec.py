from thinc.api import chain, clone, concatenate, with_array, uniqued
from thinc.api import Model, noop, with_padded
from thinc.api import Maxout, expand_window
from thinc.api import HashEmbed, StaticVectors, PyTorchLSTM
from thinc.api import residual, LayerNorm, FeatureExtractor

from ... import util
from ...util import registry, make_layer
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
def Tok2Vec(config):
    doc2feats = make_layer(config["@doc2feats"])
    embed = make_layer(config["@embed"])
    encode = make_layer(config["@encode"])
    field_size = 0
    if encode.has_attr("receptive_field"):
        field_size = encode.attrs["receptive_field"]
    tok2vec = chain(doc2feats, with_array(chain(embed, encode), pad=field_size))
    tok2vec.attrs["cfg"] = config
    tok2vec.set_dim("nO", encode.get_dim("nO"))
    tok2vec.set_ref("embed", embed)
    tok2vec.set_ref("encode", encode)
    return tok2vec


@registry.architectures.register("spacy.Doc2Feats.v1")
def Doc2Feats(config):
    columns = config["columns"]
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
    char_embed,
):
    return build_Tok2Vec_model(
        width=width,
        embed_size=embed_size,
        pretrained_vectors=pretrained_vectors,
        conv_depth=depth,
        bilstm_depth=0,
        maxout_pieces=maxout_pieces,
        window_size=window_size,
        subword_features=subword_features,
        char_embed=char_embed,
    )


@registry.architectures.register("spacy.HashEmbedBiLSTM.v1")
def hash_embed_bilstm_v1(
    pretrained_vectors, width, depth, embed_size, subword_features, char_embed
):
    return build_Tok2Vec_model(
        width=width,
        embed_size=embed_size,
        pretrained_vectors=pretrained_vectors,
        bilstm_depth=depth,
        conv_depth=0,
        maxout_pieces=0,
        window_size=1,
        subword_features=subword_features,
        char_embed=char_embed,
    )


@registry.architectures.register("spacy.MultiHashEmbed.v1")
def MultiHashEmbed(config):
    # For backwards compatibility with models before the architecture registry,
    # we have to be careful to get exactly the same model structure. One subtle
    # trick is that when we define concatenation with the operator, the operator
    # is actually binary associative. So when we write (a | b | c), we're actually
    # getting concatenate(concatenate(a, b), c). That's why the implementation
    # is a bit ugly here.
    cols = config["columns"]
    width = config["width"]
    rows = config["rows"]

    norm = HashEmbed(width, rows, column=cols.index("NORM"))
    if config["use_subwords"]:
        prefix = HashEmbed(width, rows // 2, column=cols.index("PREFIX"))
        suffix = HashEmbed(width, rows // 2, column=cols.index("SUFFIX"))
        shape = HashEmbed(width, rows // 2, column=cols.index("SHAPE"))
    if config.get("@pretrained_vectors"):
        glove = make_layer(config["@pretrained_vectors"])
    mix = make_layer(config["@mix"])

    with Model.define_operators({">>": chain, "|": concatenate}):
        if config["use_subwords"] and config["@pretrained_vectors"]:
            mix._layers[0].set_dim("nI", width * 5)
            layer = uniqued(
                (glove | norm | prefix | suffix | shape) >> mix,
                column=cols.index("ORTH"),
            )
        elif config["use_subwords"]:
            mix._layers[0].set_dim("nI", width * 4)
            layer = uniqued(
                (norm | prefix | suffix | shape) >> mix, column=cols.index("ORTH")
            )
        elif config["@pretrained_vectors"]:
            mix._layers[0].set_dim("nI", width * 2)
            layer = uniqued((glove | norm) >> mix, column=cols.index("ORTH"))
        else:
            layer = norm
    layer.attrs["cfg"] = config
    return layer


@registry.architectures.register("spacy.CharacterEmbed.v1")
def CharacterEmbed(config):
    width = config["width"]
    chars = config["chars"]

    chr_embed = _character_embed.CharacterEmbed(nM=width, nC=chars)
    other_tables = make_layer(config["@embed_features"])
    mix = make_layer(config["@mix"])

    model = chain(concatenate(chr_embed, other_tables), mix)
    model.attrs["cfg"] = config
    return model


@registry.architectures.register("spacy.MaxoutWindowEncoder.v1")
def MaxoutWindowEncoder(config):
    nO = config["width"]
    nW = config["window_size"]
    nP = config["pieces"]
    depth = config["depth"]

    cnn = (
        expand_window(window_size=nW),
        Maxout(nO=nO, nI=nO * ((nW * 2) + 1), nP=nP, dropout=0.0, normalize=True),
    )
    model = clone(residual(cnn), depth)
    model.set_dim("nO", nO)
    model.attrs["receptive_field"] = nW * depth
    return model


@registry.architectures.register("spacy.MishWindowEncoder.v1")
def MishWindowEncoder(config):
    from thinc.api import Mish

    nO = config["width"]
    nW = config["window_size"]
    depth = config["depth"]

    cnn = chain(
        expand_window(window_size=nW),
        Mish(nO=nO, nI=nO * ((nW * 2) + 1)),
        LayerNorm(nO),
    )
    model = clone(residual(cnn), depth)
    model.set_dim("nO", nO)
    return model


@registry.architectures.register("spacy.TorchBiLSTMEncoder.v1")
def TorchBiLSTMEncoder(config):
    import torch.nn

    # TODO FIX
    from thinc.api import PyTorchRNNWrapper

    width = config["width"]
    depth = config["depth"]
    if depth == 0:
        return noop()
    return with_padded(
        PyTorchRNNWrapper(torch.nn.LSTM(width, width // 2, depth, bidirectional=True))
    )


# TODO: update
_EXAMPLE_CONFIG = {
    "@doc2feats": {
        "arch": "Doc2Feats",
        "config": {"columns": ["ID", "NORM", "PREFIX", "SUFFIX", "SHAPE", "ORTH"]},
    },
    "@embed": {
        "arch": "spacy.MultiHashEmbed.v1",
        "config": {
            "width": 96,
            "rows": 2000,
            "columns": ["ID", "NORM", "PREFIX", "SUFFIX", "SHAPE", "ORTH"],
            "use_subwords": True,
            "@pretrained_vectors": {
                "arch": "TransformedStaticVectors",
                "config": {
                    "vectors_name": "en_vectors_web_lg.vectors",
                    "width": 96,
                    "column": 0,
                },
            },
            "@mix": {
                "arch": "LayerNormalizedMaxout",
                "config": {"width": 96, "pieces": 3},
            },
        },
    },
    "@encode": {
        "arch": "MaxoutWindowEncode",
        "config": {"width": 96, "window_size": 1, "depth": 4, "pieces": 3},
    },
}


def build_Tok2Vec_model(
    width,
    embed_size,
    pretrained_vectors,
    window_size,
    maxout_pieces,
    subword_features,
    char_embed,
    conv_depth,
    bilstm_depth,
) -> Model:
    if char_embed:
        subword_features = False
    cols = [ID, NORM, PREFIX, SUFFIX, SHAPE, ORTH]
    # TODO: remove hardcoded numbers from this method
    with Model.define_operators({">>": chain, "|": concatenate, "**": clone}):
        norm = HashEmbed(nO=width, nV=embed_size, column=cols.index(NORM))
        if subword_features:
            prefix = HashEmbed(nO=width, nV=embed_size // 2, column=cols.index(PREFIX))
            suffix = HashEmbed(nO=width, nV=embed_size // 2, column=cols.index(SUFFIX))
            shape = HashEmbed(nO=width, nV=embed_size // 2, column=cols.index(SHAPE))
        else:
            prefix, suffix, shape = (None, None, None)
        if pretrained_vectors is not None:
            glove = StaticVectors(
                vectors=pretrained_vectors.data,
                nO=width,
                column=cols.index(ID),
                dropout=0.0,
            )

            if subword_features:
                embed = uniqued(
                    (glove | norm | prefix | suffix | shape)
                    >> Maxout(
                        nO=width, nI=width * 5, nP=3, dropout=0.0, normalize=True
                    ),
                    column=cols.index(ORTH),
                )
            else:
                embed = uniqued(
                    (glove | norm)
                    >> Maxout(
                        nO=width, nI=width * 2, nP=3, dropout=0.0, normalize=True
                    ),
                    column=cols.index(ORTH),
                )
        elif subword_features:
            embed = uniqued(
                concatenate(norm, prefix, suffix, shape)
                >> Maxout(nO=width, nI=width * 4, nP=3, dropout=0.0, normalize=True),
                column=cols.index(ORTH),
            )
        elif char_embed:
            # TODO: move nM and nC to config
            embed = _character_embed.CharacterEmbed(nM=64, nC=8) | FeatureExtractor(
                cols
            ) >> with_array(norm)
            reduce_dimensions = Maxout(
                nO=width,
                nI=64 * 8 + width,
                nP=maxout_pieces,
                dropout=0.0,
                normalize=True,
            )
        else:
            embed = norm

        convolution = residual(
            expand_window(window_size=window_size)
            >> Maxout(
                nO=width, nI=width * 3, nP=maxout_pieces, dropout=0.0, normalize=True
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
        tok2vec.set_dim("nO", width)
        tok2vec.set_ref("embed", embed)
    return tok2vec
