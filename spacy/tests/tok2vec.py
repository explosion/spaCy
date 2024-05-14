from typing import List

from thinc.api import Model
from thinc.types import Floats2d

from spacy.tokens import Doc
from spacy.util import registry


@registry.architectures("test.LazyInitTok2Vec.v1")
def build_lazy_init_tok2vec(*, width: int) -> Model[List[Doc], List[Floats2d]]:
    """tok2vec model of which the output size is only known after
    initialization. This implementation does not output meaningful
    embeddings, it is strictly for testing."""
    return Model(
        "lazy_init_tok2vec",
        lazy_init_tok2vec_forward,
        init=lazy_init_tok2vec_init,
        dims={"nO": None},
        attrs={"width": width},
    )


def lazy_init_tok2vec_init(model: Model, X=None, Y=None):
    width = model.attrs["width"]
    model.set_dim("nO", width)


def lazy_init_tok2vec_forward(model: Model, X: List[Doc], is_train: bool):
    width = model.get_dim("nO")
    Y = [model.ops.alloc2f(len(doc), width) for doc in X]

    def backprop(dY):
        return []

    return Y, backprop
