from thinc.api import zero_init, with_array, Softmax, chain, Model

from ...util import registry


@registry.architectures.register("spacy.Tagger.v1")
def build_tagger_model(tok2vec, nO=None) -> Model:
    # TODO: glorot_uniform_init seems to work a bit better than zero_init here?!
    t2v_width = tok2vec.get_dim("nO") if tok2vec.has_dim("nO") else None
    output_layer = Softmax(nO, t2v_width, init_W=zero_init)
    softmax = with_array(output_layer)
    model = chain(tok2vec, softmax)
    model.set_ref("tok2vec", tok2vec)
    model.set_ref("softmax", output_layer)
    model.set_ref("output_layer", output_layer)
    return model
