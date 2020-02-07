from pathlib import Path

from thinc.model import Model
from thinc.layers import chain, clone, list2ragged, reduce_mean, residual
from thinc.layers import Maxout, Linear

from spacy import util
from spacy.util import registry


def default_nel_config():
    loc = Path(__file__).parent / "defaults" / "entity_linker_defaults.cfg"
    return util.load_from_config(loc, create_objects=False)


@registry.architectures.register("spacy.EntityLinker.v1")
def build_nel_encoder(entity_width, tok2vec, hidden_width):
    with Model.define_operators({">>": chain, "**": clone}):
        model = (
            tok2vec
            >> list2ragged()
            >> reduce_mean()
            >> residual(Maxout(nO=hidden_width, nI=hidden_width, nP=2, dropout=0.0))
            >> Linear(nO=entity_width, nI=hidden_width)
        )
        model.initialize()
        model.set_ref("tok2vec", tok2vec)
        model.set_dim("nO", entity_width)
    return model
