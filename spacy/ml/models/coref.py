from typing import List
from thinc.api import Model
from thinc.types import Floats2d

from ...util import registry
from ...tokens import Doc


@registry.architectures.register("spacy.Coref.v0")
def build_coref_model(
    tok2vec: Model[List[Doc], List[Floats2d]]
) -> Model:
    """Build a coref resolution model, using a provided token-to-vector component.
    TODO.

    tok2vec (Model[List[Doc], List[Floats2d]]): The token-to-vector subnetwork.
    """
    return tok2vec
