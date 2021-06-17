from typing import (
    Callable,
    Protocol,
    Iterator,
    Optional,
    Union,
    Tuple,
    Any,
)
from .doc import Doc
from .token import Token
from .underscore import Underscore
from ..lexeme import Lexeme
from ..vocab import Vocab

class SpanMethod(Protocol):
    def __call__(self: Span, *args: Any, **kwargs: Any) -> Any: ...

class Span:
    @classmethod
    def set_extension(
        cls,
        name: str,
        default: Optional[Any] = ...,
        getter: Optional[Callable[[Span], Any]] = ...,
        setter: Optional[Callable[[Span, Any], None]] = ...,
        method: Optional[SpanMethod] = ...,
        force: bool = ...,
    ) -> None: ...
    @classmethod
    def get_extension(
        cls, name: str
    ) -> Tuple[
        Optional[Any],
        Optional[SpanMethod],
        Optional[Callable[[Span], Any]],
        Optional[Callable[[Span, Any], None]],
    ]: ...
    @classmethod
    def has_extension(cls, name: str) -> bool: ...
    @classmethod
    def remove_extension(
        cls, name: str
    ) -> Tuple[
        Optional[Any],
        Optional[SpanMethod],
        Optional[Callable[[Span], Any]],
        Optional[Callable[[Span, Any], None]],
    ]: ...
    def __init__(
        self,
        doc: Doc,
        start: int,
        end: int,
        label: int = ...,
        vector: Optional[Any] = ...,
        vector_norm: Optional[float] = ...,
        kb_id: Optional[int] = ...,
    ) -> None: ...
    def __richcmp__(self, other: Span, op: int) -> bool: ...
    # TODO: Find type for hash
    def __hash__(self) -> Any: ...
    def __len__(self) -> int: ...
    def __repr__(self) -> str: ...
    def __getitem__(self, i: Union[int, Tuple[int]]) -> Span: ...
    def __iter__(self) -> Iterator[Token]: ...
    @property
    def _(self) -> Underscore: ...
    def as_doc(self, *, copy_user_data: bool = ...) -> Doc: ...
    # TODO: Find representation of ndarray
    def get_lca_matrix(self) -> Any: ...
    def similarity(self, other: Union[Doc, Span, Token, Lexeme]) -> float: ...
    @property
    def vocab(self) -> Vocab: ...
    @property
    def sent(self) -> Span: ...
    @property
    def ents(self) -> Tuple[Span]: ...
    @property
    def has_vector(self) -> bool: ...
    # TODO: Find type for ndarray
    @property
    def vector(self) -> Any: ...
    @property
    def vector_norm(self) -> float: ...
    # TODO: Find type for ndarray
    @property
    def tensor(self) -> Any: ...
    @property
    def sentiment(self) -> float: ...
    @property
    def text(self) -> str: ...
    @property
    def text_with_ws(self) -> str: ...
    @property
    def noun_chunks(self) -> Iterator[Span]: ...
    @property
    def root(self) -> Token: ...
    # TODO: Find type for ndarray
    def char_span(
        self,
        start_idx: int,
        end_idx: int,
        label: int = ...,
        kb_id: int = ...,
        vector: Optional[Any] = ...,
    ) -> Span: ...
    @property
    def conjuncts(self) -> Tuple[Token]: ...
    @property
    def lefts(self) -> Iterator[Token]: ...
    @property
    def rights(self) -> Iterator[Token]: ...
    @property
    def n_lefts(self) -> int: ...
    @property
    def n_rights(self) -> int: ...
    @property
    def subtree(self) -> Iterator[Token]: ...
    start: int
    end: int
    start_char: int
    end_char: int
    # TODO: Verify
    label: int
    # TODO: Verify
    kb_id: int
    # TODO: Verify (type for hash?)
    ent_id: Any
    ent_id_: str
    @property
    def orth_(self) -> str: ...
    @property
    def lemma_(self) -> str: ...
    label_: str
    kb_id_: str
