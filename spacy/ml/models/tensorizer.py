from pathlib import Path

from thinc.layers import Linear
from thinc.initializers import zero_init

from spacy import util
from spacy.util import registry


def default_tensorizer_config():
    loc = Path(__file__).parent / "defaults" / "tensorizer_defaults.cfg"
    return util.load_from_config(loc, create_objects=False)


@registry.architectures.register("spacy.Tensorizer.v1")
def build_tensorizer(input_size, output_size):
    input_size = util.env_opt("token_vector_width", input_size)
    return Linear(output_size, input_size, init_W=zero_init)
