from typing import Type, Callable

from thinc.layers import with_nvtx_range
from thinc.model import wrap_model_recursive

from ..language import Language
from ..pipeline import TrainablePipe
from ..util import registry


@registry.callbacks("spacy.models_with_nvtx_range.v1")
def create_models_with_nvtx_range() -> Callable[[Language], Language]:
    def models_with_nvtx_range(nlp):
        for _, component in nlp.components:
            if isinstance(component, TrainablePipe):
                component.model = wrap_model_recursive(component.model, with_nvtx_range)

        return nlp

    return models_with_nvtx_range
