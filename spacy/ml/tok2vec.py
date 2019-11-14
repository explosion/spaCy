from __future__ import unicode_literals

from thinc.api import chain, layerize, clone, concatenate, with_flatten, uniqued
from thinc.api import noop, with_square_sequences
from thinc.v2v import Maxout, Model
from thinc.i2v import HashEmbed, StaticVectors
from thinc.t2t import ExtractWindow
from thinc.misc import Residual, LayerNorm, FeatureExtracter
from ..util import make_layer, registry
from ._wire import concatenate_lists


@registry.architectures.register("spacy.Tok2Vec.v1")
def Tok2Vec(config):
    doc2feats = make_layer(config["@doc2feats"])
    embed = make_layer(config["@embed"])
    encode = make_layer(config["@encode"])
    field_size = getattr(encode, "receptive_field", 0)
    tok2vec = chain(doc2feats, with_flatten(chain(embed, encode), pad=field_size))
    tok2vec.cfg = config
    tok2vec.nO = encode.nO
    tok2vec.embed = embed
    tok2vec.encode = encode
    return tok2vec


@registry.architectures.register("spacy.Doc2Feats.v1")
def Doc2Feats(config):
    columns = config["columns"]
    return FeatureExtracter(columns)


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

    norm = HashEmbed(width, rows, column=cols.index("NORM"), name="embed_norm")
    if config["use_subwords"]:
        prefix = HashEmbed(
            width, rows // 2, column=cols.index("PREFIX"), name="embed_prefix"
        )
        suffix = HashEmbed(
            width, rows // 2, column=cols.index("SUFFIX"), name="embed_suffix"
        )
        shape = HashEmbed(
            width, rows // 2, column=cols.index("SHAPE"), name="embed_shape"
        )
    if config.get("@pretrained_vectors"):
        glove = make_layer(config["@pretrained_vectors"])
    mix = make_layer(config["@mix"])

    with Model.define_operators({">>": chain, "|": concatenate}):
        if config["use_subwords"] and config["@pretrained_vectors"]:
            mix._layers[0].nI = width * 5
            layer = uniqued(
                (glove | norm | prefix | suffix | shape) >> mix,
                column=cols.index("ORTH"),
            )
        elif config["use_subwords"]:
            mix._layers[0].nI = width * 4
            layer = uniqued(
                (norm | prefix | suffix | shape) >> mix, column=cols.index("ORTH")
            )
        elif config["@pretrained_vectors"]:
            mix._layers[0].nI = width * 2
            layer = uniqued((glove | norm) >> mix, column=cols.index("ORTH"),)
        else:
            layer = norm
    layer.cfg = config
    return layer


@registry.architectures.register("spacy.CharacterEmbed.v1")
def CharacterEmbed(config):
    from .. import _ml

    width = config["width"]
    chars = config["chars"]

    chr_embed = _ml.CharacterEmbedModel(nM=width, nC=chars)
    other_tables = make_layer(config["@embed_features"])
    mix = make_layer(config["@mix"])

    model = chain(concatenate_lists(chr_embed, other_tables), mix)
    model.cfg = config
    return model


@registry.architectures.register("spacy.MaxoutWindowEncoder.v1")
def MaxoutWindowEncoder(config):
    nO = config["width"]
    nW = config["window_size"]
    nP = config["pieces"]
    depth = config["depth"]

    cnn = chain(
        ExtractWindow(nW=nW), LayerNorm(Maxout(nO, nO * ((nW * 2) + 1), pieces=nP))
    )
    model = clone(Residual(cnn), depth)
    model.nO = nO
    model.receptive_field = nW * depth
    return model


@registry.architectures.register("spacy.MishWindowEncoder.v1")
def MishWindowEncoder(config):
    from thinc.v2v import Mish

    nO = config["width"]
    nW = config["window_size"]
    depth = config["depth"]

    cnn = chain(ExtractWindow(nW=nW), LayerNorm(Mish(nO, nO * ((nW * 2) + 1))))
    model = clone(Residual(cnn), depth)
    model.nO = nO
    return model


@registry.architectures.register("spacy.PretrainedVectors.v1")
def PretrainedVectors(config):
    return StaticVectors(config["vectors_name"], config["width"], config["column"])


@registry.architectures.register("spacy.TorchBiLSTMEncoder.v1")
def TorchBiLSTMEncoder(config):
    import torch.nn
    from thinc.extra.wrappers import PyTorchWrapperRNN

    width = config["width"]
    depth = config["depth"]
    if depth == 0:
        return layerize(noop())
    return with_square_sequences(
        PyTorchWrapperRNN(torch.nn.LSTM(width, width // 2, depth, bidirectional=True))
    )


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
