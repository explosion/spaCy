from thinc.initializers import zero_init
from thinc.layers import with_array, Softmax, chain
from thinc.model import Model

from spacy.util import registry


@registry.architectures.register("spacy.TaggerModel.v1")
def build_tagger_model(tok2vec, nr_class=None) -> Model:
    token_vector_width = tok2vec.get_dim("nO")
    # TODO: glorot_uniform_init seems to work a bit better than zero_init here?!
    softmax = with_array(Softmax(nO=nr_class, nI=token_vector_width, init_W=zero_init))
    model = chain(tok2vec, softmax)
    model.set_ref("tok2vec", tok2vec)
    model.set_ref("softmax", softmax)
    return model
