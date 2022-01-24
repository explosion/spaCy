from typing import Any, List, Dict, Tuple, Optional, Callable, Union
from typing import Iterator, Iterable, overload
from ..compat import Literal
from ..vocab import Vocab
from ..tokens import Doc, Span

class Matcher:
    def __init__(self, vocab: Vocab, validate: bool = ...) -> None: ...
    def __reduce__(self) -> Any: ...
    def __len__(self) -> int: ...
    def __contains__(self, key: str) -> bool: ...
    def add(
        self,
        key: Union[str, int],
        patterns: List[List[Dict[str, Any]]],
        *,
        on_match: Optional[
            Callable[[Matcher, Doc, int, List[Tuple[Any, ...]]], Any]
        ] = ...,
        greedy: Optional[str] = ...
    ) -> None: ...
    def remove(self, key: str) -> None: ...
    def has_key(self, key: Union[str, int]) -> bool: ...
    def get(
        self, key: Union[str, int], default: Optional[Any] = ...
    ) -> Tuple[Optional[Callable[[Any], Any]], List[List[Dict[Any, Any]]]]: ...
    def pipe(
        self,
        docs: Iterable[Tuple[Doc, Any]],
        batch_size: int = ...,
        return_matches: bool = ...,
        as_tuples: bool = ...,
    ) -> Union[
        Iterator[Tuple[Tuple[Doc, Any], Any]], Iterator[Tuple[Doc, Any]], Iterator[Doc]
    ]: ...
    @overload
    def __call__(
        self,
        doclike: Union[Doc, Span],
        *,
        as_spans: Literal[False] = ...,
        allow_missing: bool = ...,
        with_alignments: bool = ...
    ) -> List[Tuple[int, int, int]]: ...
    @overload
    def __call__(
        self,
        doclike: Union[Doc, Span],
        *,
        as_spans: Literal[True],
        allow_missing: bool = ...,
        with_alignments: bool = ...
    ) -> List[Span]: ...
    def _normalize_key(self, key: Any) -> Any: ...
