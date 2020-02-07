from pathlib import Path

from spacy import util
from spacy.morphology import Morphology
from spacy.util import registry

from thinc.model import Model
from thinc.layers import chain, add, clone, with_array, MultiSoftmax


def default_morphologizer_config():
    loc = Path(__file__).parent / "defaults" / "morphologizer_defaults.cfg"
    return util.load_from_config(loc, create_objects=False)


@registry.architectures.register("spacy.Morphologizer.v1")
def build_morphologizer_model(tok2vec):
    # TODO: where is the create_class_map() method? Or should class_nums be in config ?
    _class_map = Morphology.create_class_map()
    class_nums = _class_map.field_sizes

    token_vector_width = tok2vec.get_dim("nO")
    with Model.define_operators({">>": chain, "+": add, "**": clone}):
        softmax = with_array(MultiSoftmax(nOs=class_nums, nI=token_vector_width))
        model = tok2vec >> softmax
    model.set_ref("tok2vec", tok2vec)
    model.set_ref("softmax", softmax)
    return model
