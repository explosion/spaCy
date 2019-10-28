from __future__ import unicode_literals

from thinc.api import chain, layerize, clone, concatenate, with_flatten, uniqued
from thinc.api import noop, with_square_sequences
from thinc.v2v import Maxout
from thinc.i2v import HashEmbed, StaticVectors
from thinc.t2t import ExtractWindow
from thinc.misc import Residual, LayerNorm, FeatureExtracter

from ..util import make_layer, register_architecture
from ._wire import concatenate_lists


@register_architecture("spacy.Tok2Vec.v1")
def Tok2Vec(config):
    doc2feats = make_layer(config["@doc2feats"])
    embed = make_layer(config["@embed"])
    encode = make_layer(config["@encode"])
    depth = config["@encode"]["config"]["depth"]
    tok2vec = chain(doc2feats, with_flatten(chain(embed, encode), pad=depth))
    tok2vec.cfg = config
    tok2vec.nO = encode.nO
    tok2vec.embed = embed
    tok2vec.encode = encode
    return tok2vec


@register_architecture("spacy.Doc2Feats.v1")
def Doc2Feats(config):
    columns = config["columns"]
    return FeatureExtracter(columns)


@register_architecture("spacy.MultiHashEmbed.v1")
def MultiHashEmbed(config):
    cols = config["columns"]
    width = config["width"]
    rows = config["rows"]

    tables = [HashEmbed(width, rows, column=cols.index("NORM"), name="embed_norm")]
    if config["use_subwords"]:
        for feature in ["PREFIX", "SUFFIX", "SHAPE"]:
            tables.append(
                HashEmbed(
                    width,
                    rows // 2,
                    column=cols.index(feature),
                    name="embed_%s" % feature.lower(),
                )
            )
    if config.get("@pretrained_vectors"):
        tables.append(make_layer(config["@pretrained_vectors"]))
    mix = make_layer(config["@mix"])
    # This is a pretty ugly hack. Not sure what the best solution should be.
    mix._layers[0].nI = sum(table.nO for table in tables)
    layer = uniqued(chain(concatenate(*tables), mix), column=cols.index("ORTH"))
    layer.cfg = config
    return layer


@register_architecture("spacy.CharacterEmbed.v1")
def CharacterEmbed(config):
    width = config["width"]
    chars = config["chars"]

    chr_embed = CharacterEmbed(nM=width, nC=chars)
    other_tables = make_layer(config["@embed_features"])
    mix = make_layer(config["@mix"])

    model = chain(concatenate_lists(chr_embed, other_tables), mix)
    model.cfg = config
    return model


@register_architecture("spacy.MaxoutWindowEncoder.v1")
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
    return model


@register_architecture("spacy.PretrainedVectors.v1")
def PretrainedVectors(config):
    return StaticVectors(config["vectors_name"], config["width"], config["column"])


@register_architecture("spacy.TorchBiLSTMEncoder.v1")
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
