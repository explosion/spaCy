from thinc.layers import Linear
from thinc.initializers import zero_init

from spacy import util


def build_tensorizer(input_size=96, output_size=300):
    input_size = util.env_opt("token_vector_width", input_size)
    return Linear(output_size, input_size, init_W=zero_init)
