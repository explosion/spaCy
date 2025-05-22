from typing import Callable, List, Tuple

from thinc.api import Model, chain, with_array
from thinc.types import Floats1d, Floats2d

from ...tokens import Doc
from ...util import registry

InT = List[Doc]
OutT = Floats2d


def build_finder_model(
    tok2vec: Model[InT, List[Floats2d]], scorer: Model[OutT, OutT]
) -> Model[InT, OutT]:

    logistic_layer: Model[List[Floats2d], List[Floats2d]] = with_array(scorer)
    model: Model[InT, OutT] = chain(tok2vec, logistic_layer, flattener())
    model.set_ref("tok2vec", tok2vec)
    model.set_ref("scorer", scorer)
    model.set_ref("logistic_layer", logistic_layer)

    return model


def flattener() -> Model[List[Floats2d], Floats2d]:
    """Flattens the input to a 1-dimensional list of scores"""

    def forward(
        model: Model[Floats1d, Floats1d], X: List[Floats2d], is_train: bool
    ) -> Tuple[Floats2d, Callable[[Floats2d], List[Floats2d]]]:
        lens = model.ops.asarray1i([len(doc) for doc in X])
        Y = model.ops.flatten(X)

        def backprop(dY: Floats2d) -> List[Floats2d]:
            return model.ops.unflatten(dY, lens)

        return Y, backprop

    return Model("Flattener", forward=forward)
