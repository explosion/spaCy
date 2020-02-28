from thinc.api import chain, clone, list2ragged, reduce_mean, residual
from thinc.api import Model, Maxout, Linear

from ...util import registry


@registry.architectures.register("spacy.EntityLinker.v1")
def build_nel_encoder(tok2vec, nO=None):
    with Model.define_operators({">>": chain, "**": clone}):
        token_width = tok2vec.get_dim("nO")
        output_layer = Linear(nO=nO, nI=token_width)
        model = (
            tok2vec
            >> list2ragged()
            >> reduce_mean()
            >> residual(Maxout(nO=token_width, nI=token_width, nP=2, dropout=0.0))
            >> output_layer
        )
        model.set_ref("output_layer", output_layer)
        model.set_ref("tok2vec", tok2vec)
    return model
