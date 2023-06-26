from typing import Any, Callable, Dict, List, Literal, Optional, Tuple, Union, overload

from ..tokens import Doc, Span
from ..vocab import Vocab
from .matcher import Matcher

class PhraseMatcher:
    def __init__(
        self, vocab: Vocab, attr: Optional[Union[int, str]] = ..., validate: bool = ...
    ) -> None: ...
    def __reduce__(self) -> Any: ...
    def __len__(self) -> int: ...
    def __contains__(self, key: str) -> bool: ...
    def add(
        self,
        key: str,
        docs: List[Doc],
        *,
        on_match: Optional[
            Callable[[Matcher, Doc, int, List[Tuple[Any, ...]]], Any]
        ] = ...,
    ) -> None: ...
    def _add_from_arrays(
        self,
        key: str,
        specs: List[List[int]],
        *,
        on_match: Optional[
            Callable[[Matcher, Doc, int, List[Tuple[Any, ...]]], Any]
        ] = ...,
    ) -> None: ...
    def remove(self, key: str) -> None: ...
    @overload
    def __call__(
        self,
        doclike: Union[Doc, Span],
        *,
        as_spans: Literal[False] = ...,
    ) -> List[Tuple[int, int, int]]: ...
    @overload
    def __call__(
        self,
        doclike: Union[Doc, Span],
        *,
        as_spans: Literal[True],
    ) -> List[Span]: ...
