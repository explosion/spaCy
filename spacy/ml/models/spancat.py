from typing import List, Tuple
from thinc.api import Model, with_getitem, chain, list2ragged, Logistic
from thinc.api import Maxout
from thinc.types import Ragged, Floats2d
from ...util import registry
from ...tokens import Doc
from ..extract_spans import extract_spans


@registry.architectures.register("spacy.MaxoutLogistic.v1")
def build_MaxoutLogistic(nI=None, nO=None, pieces=3):
    return chain(Maxout(nI=nI, nO=nO, pieces=pieces), Logistic())


@registry.architectures.register("spacy.SpanCategorizer.v1")
def build_spancat_model(
    tok2vec: Model[List[Doc], List[Floats2d]],
    reducer: Model[Ragged, Floats2d],
    scorer: Model[Floats2d, Floats2d]
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
