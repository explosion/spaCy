from thinc.api import Linear, zero_init

from ... import util
from ...util import registry


@registry.architectures.register("spacy.Tensorizer.v1")
def build_tensorizer(input_size, output_size):
    input_size = util.env_opt("token_vector_width", input_size)
    return Linear(output_size, input_size, init_W=zero_init)
