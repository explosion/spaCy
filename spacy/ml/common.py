
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
    layer = chain(Maxout(width, pieces=pieces), LayerNorm(nO=width))
    layer.nO = width
    return layer
