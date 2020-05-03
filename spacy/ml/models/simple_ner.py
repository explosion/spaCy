from typing import List, Tuple, Dict, Optional
from thinc.api import Ops, Model, Mish, with_array, softmax_activation, padded2list
from thinc.api import chain, list2padded
from thinc.types import Padded, Ints1d, Ints3d, Floats2d, Floats3d

from ...tokens import Doc
from .._biluo import BILUO
from ...util import registry


@registry.architectures.register("spacy.BiluoTagger.v1")
def BiluoTagger(tok2vec: Model[List[Doc], List[Floats2d]], labels: Optional[List[str]]=None) -> Model[List[Doc], List[Floats2d]]:
    labels = ["PERSON", "LOC"]
    biluo = BILUO(labels=labels)
    n_actions = biluo.get_dim("nO") if biluo.has_dim("nO") else None
    model = chain(
        tok2vec,
        list2padded(),
        with_array(Mish(nO=n_actions, nI=tok2vec.get_dim("nO"))),
        biluo,
        with_array(softmax_activation()),
        padded2list()
    )
    model.set_ref("biluo", biluo)
    assert model is not None
    return model


__all__ = ["BiluoTagger"]
