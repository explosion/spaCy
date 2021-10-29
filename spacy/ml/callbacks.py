from functools import partial
from typing import Type, Callable, TYPE_CHECKING

from thinc.layers import with_nvtx_range
from thinc.model import Model, wrap_model_recursive

from ..util import registry

if TYPE_CHECKING:
    # This lets us add type hints for mypy etc. without causing circular imports
    from ..language import Language  # noqa: F401


@registry.callbacks("spacy.models_with_nvtx_range.v1")
def create_models_with_nvtx_range(
    forward_color: int = -1, backprop_color: int = -1
) -> Callable[["Language"], "Language"]:
    def models_with_nvtx_range(nlp):
        pipes = [
            pipe
            for _, pipe in nlp.components
            if hasattr(pipe, "is_trainable") and pipe.is_trainable
        ]

        # We need process all models jointly to avoid wrapping callbacks twice.
        models = Model(
            "wrap_with_nvtx_range",
            forward=lambda model, X, is_train: ...,
            layers=[pipe.model for pipe in pipes],
        )

        for node in models.walk():
            with_nvtx_range(
                node, forward_color=forward_color, backprop_color=backprop_color
            )

        return nlp

    return models_with_nvtx_range
