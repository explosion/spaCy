import functools
from typing import List, Tuple, Dict, Optional
from thinc.api import Ops, Model, Linear, with_array, softmax_activation, padded2list
from thinc.api import chain, list2padded
from thinc.types import Padded, Ints1d, Ints3d, Floats2d, Floats3d

from ...tokens import Doc
from .._biluo import BILUO
from ...util import registry


@registry.architectures.register("spacy.BiluoTagger.v1")
def BiluoTagger(tok2vec: Model[List[Doc], List[Floats2d]]) -> Model[List[Doc], List[Floats2d]]:
    biluo = BILUO()
    linear = Linear(nO=None, nI=tok2vec.get_dim("nO"))
    model = chain(
        tok2vec,
        list2padded(),
        with_array(linear),
        biluo,
        with_array(softmax_activation()),
        padded2list()
    )

    return Model(
        "biluo-tagger",
        forward,
        init=init,
        layers=[model],
        refs={"tok2vec": tok2vec, "linear": linear, "biluo": biluo},
        dims={"nO": None},
        attrs={"get_num_actions": biluo.attrs["get_num_actions"]}
    )


def init(model: Model[List[Doc], List[Floats2d]], X=None, Y=None) -> None:
    if model.get_dim("nO") is None and Y:
        model.set_dim("nO", Y[0].shape[1])
    nO = model.get_dim("nO")
    biluo = model.get_ref("biluo")
    linear = model.get_ref("linear")
    biluo.set_dim("nO", nO)
    linear.set_dim("nO", nO)
    model.layers[0].initialize(X=X, Y=Y)


def forward(model: Model, X: List[Doc], is_train: bool):
    return model.layers[0](X, is_train)


__all__ = ["BiluoTagger"]
