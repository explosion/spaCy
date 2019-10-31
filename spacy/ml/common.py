from __future__ import unicode_literals

from thinc.api import chain
from thinc.v2v import Maxout
from thinc.misc import LayerNorm
from ..util import register_architecture, make_layer


@register_architecture("thinc.FeedForward.v1")
def FeedForward(config):
    layers = [make_layer(layer_cfg) for layer_cfg in config["layers"]]
    model = chain(*layers)
    model.cfg = config
    return model


@register_architecture("spacy.LayerNormalizedMaxout.v1")
def LayerNormalizedMaxout(config):
    width = config["width"]
    pieces = config["pieces"]
    layer = LayerNorm(Maxout(width, pieces=pieces))
    layer.nO = width
    return layer
