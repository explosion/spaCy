from typing import List, Tuple, Union, Optional, Callable, Any, Dict, overload
from ..compat import Literal
from .matcher import Matcher
from ..vocab import Vocab
from ..tokens import Doc, Span

class PhraseMatcher:
    def __init__(
        self, vocab: Vocab, attr: Optional[Union[int, str]], validate: bool = ...
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
