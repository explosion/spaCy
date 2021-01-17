from typing import List, Tuple
from thinc.api import Model, with_getitem, chain, list2ragged
from thinc.types import Ragged, Floats2d
from ...tokens import Doc
from ..extract_spans import extract_spans


def build_spancat_model(
    tok2vec: Model[List[Doc], List[Floats2d]],
    reducer: Model[Ragged, Floats2d],
    scorer: Model[Floats2d, Floats2d]
) -> Model[Tuple[List[Doc], Ragged], Floats2d]:
    """Constrct a span categorizer model out of three submodels: a tok2vec model,
    to map each token in the batch to a vector, a reducer, to map each subsequence
    to a single vector, and a scorer, to map the vectors to category probabilities.
    The submodels are all set as named references.

    tok2vec (Model[List[Doc], List[Floats2d]]): The tok2vec model.
    reducer (Model[Ragged, Floats2d]): The reducer model.
    scorer (Model[Floats2d, Floats2d]): The scorer model.
    """
    model = chain(
        with_getitem(0, chain(tok2vec, list2ragged())),
        extract_spans(),
        reducer,
        scorer
    )
    model.set_ref("tok2vec", tok2vec)
    model.set_ref("reducer", reducer)
    model.set_ref("scorer", scorer)
    return model
