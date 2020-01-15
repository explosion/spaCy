from thinc.layers import chain, Maxout, LayerNorm
from thinc.model import Model
from ..util import registry, make_layer


@registry.architectures.register("thinc.FeedForward.v1")
def FeedForward(config):
    layers = [make_layer(layer_cfg) for layer_cfg in config["layers"]]
    model = chain(*layers)
    model.set_attr("cfg", config)
    return model


@registry.architectures.register("spacy.LayerNormalizedMaxout.v1")
def LayerNormalizedMaxout(config):
    width = config["width"]
    pieces = config["pieces"]
    with Model.define_operators({">>": chain}):
        layer = Maxout(nO=width, nP=pieces, dropout=0.0, normalize=True)
    return layer
