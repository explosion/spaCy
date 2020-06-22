from typing import List
from thinc.api import Model, Linear, with_array, softmax_activation, padded2list
from thinc.api import chain, list2padded, configure_normal_init
from thinc.api import Dropout
from thinc.types import Floats2d

from ...tokens import Doc
from .._biluo import BILUO
from .._iob import IOB
from ...util import registry


@registry.architectures.register("spacy.BiluoTagger.v1")
def BiluoTagger(
    tok2vec: Model[List[Doc], List[Floats2d]]
) -> Model[List[Doc], List[Floats2d]]:
    biluo = BILUO()
    linear = Linear(
        nO=None, nI=tok2vec.get_dim("nO"), init_W=configure_normal_init(mean=0.02)
    )
    model = chain(
        tok2vec,
        list2padded(),
        with_array(chain(Dropout(0.1), linear)),
        biluo,
        with_array(softmax_activation()),
        padded2list(),
    )

    return Model(
        "biluo-tagger",
        forward,
        init=init,
        layers=[model, linear],
        refs={"tok2vec": tok2vec, "linear": linear, "biluo": biluo},
        dims={"nO": None},
        attrs={"get_num_actions": biluo.attrs["get_num_actions"]},
    )


@registry.architectures.register("spacy.IOBTagger.v1")
def IOBTagger(
    tok2vec: Model[List[Doc], List[Floats2d]]
) -> Model[List[Doc], List[Floats2d]]:
    biluo = IOB()
    linear = Linear(nO=None, nI=tok2vec.get_dim("nO"))
    model = chain(
        tok2vec,
        list2padded(),
        with_array(linear),
        biluo,
        with_array(softmax_activation()),
        padded2list(),
    )

    return Model(
        "iob-tagger",
        forward,
        init=init,
        layers=[model],
        refs={"tok2vec": tok2vec, "linear": linear, "biluo": biluo},
        dims={"nO": None},
        attrs={"get_num_actions": biluo.attrs["get_num_actions"]},
    )


def init(model: Model[List[Doc], List[Floats2d]], X=None, Y=None) -> None:
    if model.get_dim("nO") is None and Y:
        model.set_dim("nO", Y[0].shape[1])
    nO = model.get_dim("nO")
    biluo = model.get_ref("biluo")
    linear = model.get_ref("linear")
    biluo.set_dim("nO", nO)
    if linear.has_dim("nO") is None:
        linear.set_dim("nO", nO)
    model.layers[0].initialize(X=X, Y=Y)


def forward(model: Model, X: List[Doc], is_train: bool):
    return model.layers[0](X, is_train)


__all__ = ["BiluoTagger"]
