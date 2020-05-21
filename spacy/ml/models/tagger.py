from thinc.api import zero_init, with_array, Softmax, chain, Model, Dropout
from thinc.api import glorot_uniform_init

from ...util import registry


@registry.architectures.register("spacy.Tagger.v1")
def build_tagger_model(tok2vec, nO=None) -> Model:
    token_vector_width = tok2vec.get_dim("nO")
    # TODO: glorot_uniform_init seems to work a bit better than zero_init here?!
    output_layer = Softmax(nO, nI=token_vector_width, init_W=zero_init)
    softmax = with_array(output_layer)
    model = chain(tok2vec, softmax)
    model.set_ref("tok2vec", tok2vec)
    model.set_ref("softmax", output_layer)
    model.set_ref("output_layer", output_layer)
    return model
