import functools
import inspect
import types
from typing import Type, Callable, Dict, TYPE_CHECKING, List, Optional
import warnings
from spacy.errors import Warnings

from thinc.layers import with_nvtx_range
from thinc.model import Model, wrap_model_recursive
from thinc.util import use_nvtx_range

from ..util import registry

if TYPE_CHECKING:
    # This lets us add type hints for mypy etc. without causing circular imports
    from ..language import Language  # noqa: F401


DEFAULT_ANNOTATABLE_PIPE_METHODS = [
    "pipe",
    "predict",
    "set_annotations",
    "update",
    "rehearse",
    "get_loss",
    "initialize",
    "begin_update",
    "finish_update",
    "update",
]


def models_with_nvtx_range(nlp, forward_color: int, backprop_color: int):
    pipes = [
        pipe
        for _, pipe in nlp.components
        if hasattr(pipe, "is_trainable") and pipe.is_trainable
    ]

    # We need process all models jointly to avoid wrapping callbacks twice.
    models: Model = Model(
        "wrap_with_nvtx_range",
        forward=lambda model, X, is_train: ...,
        layers=[pipe.model for pipe in pipes],
    )

    for node in models.walk():
        with_nvtx_range(
            node, forward_color=forward_color, backprop_color=backprop_color
        )

    return nlp


@registry.callbacks("spacy.models_with_nvtx_range.v1")
def create_models_with_nvtx_range(
    forward_color: int = -1, backprop_color: int = -1
) -> Callable[["Language"], "Language"]:
    return functools.partial(
        models_with_nvtx_range,
        forward_color=forward_color,
        backprop_color=backprop_color,
    )


def nvtx_range_wrapper_for_pipe_method(self, func, *args, **kwargs):
    func_name = (
        func.func.__name__ if isinstance(func, functools.partial) else func.__name__
    )

    with use_nvtx_range(f"pipe '{self.name}' - {func_name}"):
        return func(*args, **kwargs)


def pipes_with_nvtx_range(
    nlp, additional_pipe_functions: Optional[Dict[str, List[str]]]
):
    for _, pipe in nlp.components:
        if additional_pipe_functions:
            extra_funcs = additional_pipe_functions.get(pipe.name, [])
        else:
            extra_funcs = []

        for name in DEFAULT_ANNOTATABLE_PIPE_METHODS + extra_funcs:
            func = getattr(pipe, name, None)
            if func is None:
                if name not in DEFAULT_ANNOTATABLE_PIPE_METHODS:
                    warnings.warn(Warnings.W121.format(method=name, pipe=pipe.name))
                continue

            wrapped_func = functools.partial(
                types.MethodType(nvtx_range_wrapper_for_pipe_method, pipe), func
            )

            # Try to preserve the original function signature.
            try:
                wrapped_func.__signature__ = inspect.signature(func)  # type: ignore
            except:
                pass

            try:
                setattr(
                    pipe,
                    name,
                    wrapped_func,
                )
            except AttributeError:
                warnings.warn(Warnings.W122.format(method=name, pipe=pipe.name))

    return nlp


@registry.callbacks("spacy.models_and_pipes_with_nvtx_range.v1")
def create_models_and_pipes_with_nvtx_range(
    forward_color: int = -1,
    backprop_color: int = -1,
    additional_pipe_functions: Optional[Dict[str, List[str]]] = None,
) -> Callable[["Language"], "Language"]:
    def inner(nlp):
        nlp = models_with_nvtx_range(nlp, forward_color, backprop_color)
        nlp = pipes_with_nvtx_range(nlp, additional_pipe_functions)
        return nlp

    return inner
