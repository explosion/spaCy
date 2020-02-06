from thinc.model import Model
from thinc.layers import chain, add, clone, with_array, MultiSoftmax


def default_morphologizer_config(tok2vec_config=None):
    raise NotImplementedError()

# TODO: previous tok2vec defaults: char_embed=True, embed_size=7000, token_vector_width=128
def build_morphologizer_model(tok2vec, class_nums, pretrained_vectors, **cfg):
    token_vector_width = tok2vec.get_dim("nO")
    with Model.define_operators({">>": chain, "+": add, "**": clone}):
        softmax = with_array(MultiSoftmax(nOs=class_nums, nI=token_vector_width))
        model = tok2vec >> softmax
    model.set_ref("tok2vec", tok2vec)
    model.set_ref("softmax", softmax)
    return model
