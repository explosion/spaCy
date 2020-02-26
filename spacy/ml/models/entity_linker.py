from pathlib import Path

from thinc.model import Model
from thinc.layers import chain, clone, list2ragged, reduce_mean, residual
from thinc.layers import Maxout, Linear

from spacy import util
from spacy.util import registry


def default_nel():
    loc = Path(__file__).parent / "defaults" / "entity_linker_defaults.cfg"
    return util.load_from_config(loc, create_objects=True)["model"]


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
