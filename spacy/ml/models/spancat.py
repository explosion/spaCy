from typing import List, Tuple
from thinc.api import Model, with_getitem, chain, list2ragged, Logistic
from thinc.api import Maxout, Linear, concatenate, glorot_uniform_init
from thinc.api import reduce_mean, reduce_max, reduce_first, reduce_last
from thinc.types import Ragged, Floats2d

from ...util import registry
from ...tokens import Doc
from ..extract_spans import extract_spans


@registry.layers.register("spacy.LinearLogistic.v1")
def build_linear_logistic(nO=None, nI=None) -> Model[Floats2d, Floats2d]:
    """An output layer for multi-label classification. It uses a linear layer
    followed by a logistic activation.
    """
    return chain(Linear(nO=nO, nI=nI, init_W=glorot_uniform_init), Logistic())


@registry.layers.register("spacy.mean_max_reducer.v1")
def build_mean_max_reducer(hidden_size: int) -> Model[Ragged, Floats2d]:
    """Reduce sequences by concatenating their mean and max pooled vectors,
    and then combine the concatenated vectors with a hidden layer.
    """
    return chain(
        concatenate(reduce_last(), reduce_first(), reduce_mean(), reduce_max()),
        Maxout(nO=hidden_size, normalize=True, dropout=0.0),
    )


@registry.architectures.register("spacy.SpanCategorizer.v1")
def build_spancat_model(
    tok2vec: Model[List[Doc], List[Floats2d]],
    reducer: Model[Ragged, Floats2d],
    scorer: Model[Floats2d, Floats2d],
) -> Model[Tuple[List[Doc], Ragged], Floats2d]:
    """Build a span categorizer model, given a token-to-vector model, a
    reducer model to map the sequence of vectors for each span down to a single
    vector, and a scorer model to map the vectors to probabilities.

    tok2vec (Model[List[Doc], List[Floats2d]]): The tok2vec model.
    reducer (Model[Ragged, Floats2d]): The reducer model.
    scorer (Model[Floats2d, Floats2d]): The scorer model.
    """
    model = chain(
        with_getitem(0, chain(tok2vec, list2ragged())),
        extract_spans(),
        reducer,
        scorer,
    )
    model.set_ref("tok2vec", tok2vec)
    model.set_ref("reducer", reducer)
    model.set_ref("scorer", scorer)
    return model
