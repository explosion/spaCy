from typing import Type, Callable

from thinc.layers import with_nvtx_range
from thinc.model import Model, wrap_model_recursive

from ..language import Language
from ..pipeline import TrainablePipe
from ..util import registry


@registry.callbacks("spacy.models_with_nvtx_range.v1")
def create_models_with_nvtx_range() -> Callable[[Language], Language]:
    def models_with_nvtx_range(nlp):
        pipes = [pipe for _, pipe in nlp.components if isinstance(pipe, TrainablePipe)]

        # We need to wrap all models jointly to avoid double-wrapping.
        models = Model(
            "wrap_with_nvtx_range",
            forward=lambda model, X, is_train: ...,
            layers=[pipe.model for pipe in pipes],
        )
        models = wrap_model_recursive(models, with_nvtx_range)

        wrapped_models = models.layers[0].layers

        assert len(wrapped_models) == len(pipes)

        for (model, pipe) in zip(wrapped_models, pipes):
            pipe.model = model

        return nlp

    return models_with_nvtx_range
