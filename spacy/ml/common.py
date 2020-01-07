from thinc.layers import chain, Maxout, LayerNorm
from ..util import registry, make_layer


@registry.architectures.register("thinc.FeedForward.v1")
def FeedForward(config):
    layers = [make_layer(layer_cfg) for layer_cfg in config["layers"]]
    model = chain(*layers)
    model.cfg = config
    return model


@registry.architectures.register("spacy.LayerNormalizedMaxout.v1")
def LayerNormalizedMaxout(config):
    width = config["width"]
    pieces = config["pieces"]
    layer = Maxout(nO=width, nP=pieces) >> LayerNorm(nO=width)
    return layer
