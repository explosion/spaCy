from thinc.initializers import zero_init
from thinc.layers import with_array, Softmax, chain
from thinc.model import Model

from spacy.util import registry


@registry.architectures.register("spacy.Tagger.v1")
def build_tagger_model(tok2vec, nO=None) -> Model:
    token_vector_width = tok2vec.get_dim("nO")
    # TODO: glorot_uniform_init seems to work a bit better than zero_init here?!
    output_layer = Softmax(nO, nI=token_vector_width, init_W=zero_init)
    softmax = with_array(output_layer)
    model = chain(tok2vec, softmax)
    model.set_ref("tok2vec", tok2vec)
    model.set_ref("softmax", softmax)
    model.set_ref("output_layer", output_layer)
    return model
