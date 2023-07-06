from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Protocol,
    Tuple,
    Union,
    overload,
)

import numpy as np
from cymem.cymem import Pool
from thinc.types import Floats1d, Floats2d, Ints2d

from ..lexeme import Lexeme
from ..vocab import Vocab
from ._dict_proxies import SpanGroups
from ._retokenize import Retokenizer
from .span import Span
from .token import Token
from .underscore import Underscore

DOCBIN_ALL_ATTRS: Tuple[str, ...]

class DocMethod(Protocol):
    def __call__(self: Doc, *args: Any, **kwargs: Any) -> Any: ...  # type: ignore[misc]

class Doc:
    vocab: Vocab
    mem: Pool
    spans: SpanGroups
    max_length: int
    length: int
    sentiment: float
    cats: Dict[str, float]
    user_hooks: Dict[str, Callable[..., Any]]
    user_token_hooks: Dict[str, Callable[..., Any]]
    user_span_hooks: Dict[str, Callable[..., Any]]
    tensor: np.ndarray[Any, np.dtype[np.float_]]
    user_data: Dict[str, Any]
    has_unknown_spaces: bool
    _context: Any
    @classmethod
    def set_extension(
        cls,
        name: str,
        default: Optional[Any] = ...,
        getter: Optional[Callable[[Doc], Any]] = ...,
        setter: Optional[Callable[[Doc, Any], None]] = ...,
        method: Optional[DocMethod] = ...,
        force: bool = ...,
    ) -> None: ...
    @classmethod
    def get_extension(
        cls, name: str
    ) -> Tuple[
        Optional[Any],
        Optional[DocMethod],
        Optional[Callable[[Doc], Any]],
        Optional[Callable[[Doc, Any], None]],
    ]: ...
    @classmethod
    def has_extension(cls, name: str) -> bool: ...
    @classmethod
    def remove_extension(
        cls, name: str
    ) -> Tuple[
        Optional[Any],
        Optional[DocMethod],
        Optional[Callable[[Doc], Any]],
        Optional[Callable[[Doc, Any], None]],
    ]: ...
    def __init__(
        self,
        vocab: Vocab,
        words: Optional[List[str]] = ...,
        spaces: Optional[List[bool]] = ...,
        user_data: Optional[Dict[Any, Any]] = ...,
        tags: Optional[List[str]] = ...,
        pos: Optional[List[str]] = ...,
        morphs: Optional[List[str]] = ...,
        lemmas: Optional[List[str]] = ...,
        heads: Optional[List[int]] = ...,
        deps: Optional[List[str]] = ...,
        sent_starts: Optional[List[Union[bool, int, None]]] = ...,
        ents: Optional[List[str]] = ...,
    ) -> None: ...
    @property
    def _(self) -> Underscore: ...
    @property
    def is_tagged(self) -> bool: ...
    @property
    def is_parsed(self) -> bool: ...
    @property
    def is_nered(self) -> bool: ...
    @property
    def is_sentenced(self) -> bool: ...
    def has_annotation(
        self, attr: Union[int, str], *, require_complete: bool = ...
    ) -> bool: ...
    @overload
    def __getitem__(self, i: int) -> Token: ...
    @overload
    def __getitem__(self, i: slice) -> Span: ...
    def __iter__(self) -> Iterator[Token]: ...
    def __len__(self) -> int: ...
    def __unicode__(self) -> str: ...
    def __bytes__(self) -> bytes: ...
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...
    @property
    def doc(self) -> Doc: ...
    def char_span(
        self,
        start_idx: int,
        end_idx: int,
        label: Union[int, str] = ...,
        kb_id: Union[int, str] = ...,
        vector: Optional[Floats1d] = ...,
        alignment_mode: str = ...,
        span_id: Union[int, str] = ...,
    ) -> Span: ...
    def similarity(self, other: Union[Doc, Span, Token, Lexeme]) -> float: ...
    @property
    def has_vector(self) -> bool: ...
    vector: Floats1d
    vector_norm: float
    @property
    def text(self) -> str: ...
    @property
    def text_with_ws(self) -> str: ...
    ents: Tuple[Span]
    def set_ents(
        self,
        entities: List[Span],
        *,
        blocked: Optional[List[Span]] = ...,
        missing: Optional[List[Span]] = ...,
        outside: Optional[List[Span]] = ...,
        default: str = ...
    ) -> None: ...
    @property
    def noun_chunks(self) -> Iterator[Span]: ...
    @property
    def sents(self) -> Iterator[Span]: ...
    @property
    def lang(self) -> int: ...
    @property
    def lang_(self) -> str: ...
    def count_by(
        self, attr_id: int, exclude: Optional[Any] = ..., counts: Optional[Any] = ...
    ) -> Dict[Any, int]: ...
    def from_array(
        self, attrs: Union[int, str, List[Union[int, str]]], array: Ints2d
    ) -> Doc: ...
    def to_array(
        self, py_attr_ids: Union[int, str, List[Union[int, str]]]
    ) -> np.ndarray[Any, np.dtype[np.float_]]: ...
    @staticmethod
    def from_docs(
        docs: List[Doc],
        ensure_whitespace: bool = ...,
        attrs: Optional[Union[Tuple[Union[str, int]], List[Union[int, str]]]] = ...,
    ) -> Doc: ...
    def get_lca_matrix(self) -> Ints2d: ...
    def copy(self) -> Doc: ...
    def to_disk(
        self, path: Union[str, Path], *, exclude: Iterable[str] = ...
    ) -> None: ...
    def from_disk(
        self, path: Union[str, Path], *, exclude: Union[List[str], Tuple[str]] = ...
    ) -> Doc: ...
    def to_bytes(self, *, exclude: Union[List[str], Tuple[str]] = ...) -> bytes: ...
    def from_bytes(
        self, bytes_data: bytes, *, exclude: Union[List[str], Tuple[str]] = ...
    ) -> Doc: ...
    def to_dict(self, *, exclude: Union[List[str], Tuple[str]] = ...) -> bytes: ...
    def from_dict(
        self, msg: bytes, *, exclude: Union[List[str], Tuple[str]] = ...
    ) -> Doc: ...
    def extend_tensor(self, tensor: Floats2d) -> None: ...
    def retokenize(self) -> Retokenizer: ...
    def to_json(self, underscore: Optional[List[str]] = ...) -> Dict[str, Any]: ...
    def from_json(
        self, doc_json: Dict[str, Any] = ..., validate: bool = False
    ) -> Doc: ...
    def to_utf8_array(self, nr_char: int = ...) -> Ints2d: ...
    @staticmethod
    def _get_array_attrs() -> Tuple[Any]: ...
