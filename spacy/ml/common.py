from __future__ import unicode_literals

from thinc.api import chain
from thinc.v2v import Maxout
from thinc.misc import LayerNorm
from ..util import Registry, make_layer


@Registry.architectures.register("thinc.FeedForward.v1")
def FeedForward(config):
    layers = [make_layer(layer_cfg) for layer_cfg in config["layers"]]
    model = chain(*layers)
    model.cfg = config
    return model


@Registry.architectures.register("spacy.LayerNormalizedMaxout.v1")
def LayerNormalizedMaxout(config):
    width = config["width"]
    pieces = config["pieces"]
    layer = LayerNorm(Maxout(width, pieces=pieces))
    layer.nO = width
    return layer
