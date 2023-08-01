from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Sequence,
)

from thinc.api import Model, Optimizer

from .compat import Protocol, runtime_checkable

if TYPE_CHECKING:
    from .language import Language
    from .training import Example


@runtime_checkable
class TrainableComponent(Protocol):
    model: Any
    is_trainable: bool

    def update(
        self,
        examples: Iterable["Example"],
        *,
        drop: float = 0.0,
        sgd: Optional[Optimizer] = None,
        losses: Optional[Dict[str, float]] = None
    ) -> Dict[str, float]:
        ...

    def finish_update(self, sgd: Optimizer) -> None:
        ...


@runtime_checkable
class InitializableComponent(Protocol):
    def initialize(
        self,
        get_examples: Callable[[], Iterable["Example"]],
        nlp: "Language",
        **kwargs: Any
    ):
        ...


@runtime_checkable
class ListenedToComponent(Protocol):
    model: Any
    listeners: Sequence[Model]
    listener_map: Dict[str, Sequence[Model]]
    listening_components: List[str]

    def add_listener(self, listener: Model, component_name: str) -> None:
        ...

    def remove_listener(self, listener: Model, component_name: str) -> bool:
        ...

    def find_listeners(self, component) -> None:
        ...
