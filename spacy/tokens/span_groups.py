from typing import Dict, Iterable, List, Tuple, Union, Optional, TYPE_CHECKING
import warnings
import weakref
from collections import UserDict
import srsly

from .span_group import SpanGroup
from ..errors import Errors, Warnings


if TYPE_CHECKING:
    # This lets us add type hints for mypy etc. without causing circular imports
    from .doc import Doc  # noqa: F401
    from .span import Span  # noqa: F401


# Why inherit from UserDict instead of dict here?
# Well, the 'dict' class doesn't necessarily delegate everything nicely,
# for performance reasons. The UserDict is slower but better behaved.
# See https://treyhunner.com/2019/04/why-you-shouldnt-inherit-from-list-and-dict-in-python/
class SpanGroups(UserDict):
    """A dict-like proxy held by the Doc, to control access to span groups."""

    _EMPTY_BYTES = srsly.msgpack_dumps([])

    def __init__(
        self, doc: "Doc", items: Iterable[Tuple[str, SpanGroup]] = tuple()
    ) -> None:
        self.doc_ref = weakref.ref(doc)
        UserDict.__init__(self, items)  # type: ignore[arg-type]

    def __setitem__(self, key: str, value: Union[SpanGroup, Iterable["Span"]]) -> None:
        if not isinstance(value, SpanGroup):
            value = self._make_span_group(key, value)
        assert value.doc is self.doc_ref()
        UserDict.__setitem__(self, key, value)

    def _make_span_group(self, name: str, spans: Iterable["Span"]) -> SpanGroup:
        doc = self._ensure_doc()
        return SpanGroup(doc, name=name, spans=spans)

    def copy(self, doc: Optional["Doc"] = None) -> "SpanGroups":
        if doc is None:
            doc = self._ensure_doc()
        data_copy = ((k, v.copy(doc=doc)) for k, v in self.items())
        return SpanGroups(doc, items=data_copy)

    def setdefault(self, key, default=None):
        if not isinstance(default, SpanGroup):
            if default is None:
                spans = []
            else:
                spans = default
            default = self._make_span_group(key, spans)
        return super().setdefault(key, default=default)

    def to_bytes(self) -> bytes:
        # We serialize this as a dict in order to track the key(s) a SpanGroup
        # is a value of (in a backward- and forward-compatible way), since
        # a SpanGroup can have a key that doesn't match its `.name` (See #10685)
        if len(self) == 0:
            return self._EMPTY_BYTES
        msg: Dict[bytes, List[str]] = {}
        for key, value in self.items():
            msg.setdefault(value.to_bytes(), []).append(key)
        return srsly.msgpack_dumps(msg)

    def from_bytes(self, bytes_data: bytes) -> "SpanGroups":
        # backwards-compatibility: bytes_data may be one of:
        # b'', a serialized empty list, a serialized list of SpanGroup bytes
        # or a serialized dict of SpanGroup bytes -> keys
        msg = (
            []
            if not bytes_data or bytes_data == self._EMPTY_BYTES
            else srsly.msgpack_loads(bytes_data)
        )
        self.clear()
        doc = self._ensure_doc()
        if isinstance(msg, list):
            # This is either the 1st version of `SpanGroups` serialization
            # or there were no SpanGroups serialized
            for value_bytes in msg:
                group = SpanGroup(doc).from_bytes(value_bytes)
                if group.name in self:
                    # Display a warning if `msg` contains `SpanGroup`s
                    # that have the same .name (attribute).
                    # Because, for `SpanGroups` serialized as lists,
                    # only 1 SpanGroup per .name is loaded. (See #10685)
                    warnings.warn(
                        Warnings.W120.format(
                            group_name=group.name, group_values=self[group.name]
                        )
                    )
                self[group.name] = group
        else:
            for value_bytes, keys in msg.items():
                group = SpanGroup(doc).from_bytes(value_bytes)
                # Deserialize `SpanGroup`s as copies because it's possible for two
                # different `SpanGroup`s (pre-serialization) to have the same bytes
                # (since they can have the same `.name`).
                self[keys[0]] = group
                for key in keys[1:]:
                    self[key] = group.copy()
        return self

    def _ensure_doc(self) -> "Doc":
        doc = self.doc_ref()
        if doc is None:
            raise ValueError(Errors.E866)
        return doc
