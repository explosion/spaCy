from typing import Iterable, Tuple, Union, Optional, TYPE_CHECKING
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
# See https://treyhunner.com/2019/04/why-you-shouldnt-inherit-from-list-and-dict-in-python/0ww
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
        return SpanGroups(doc).from_bytes(self.to_bytes())

    def to_bytes(self) -> bytes:
        # We don't need to serialize this as a dict, because each group has
        # a name. However the group names may not match the keys, so fix the
        # names in internal copies before serializing if necessary. (See #10685)
        if len(self) == 0:
            return self._EMPTY_BYTES
        renamed_groups = dict(self.items())
        for key, group in renamed_groups.items():
            if key != group.name:
                renamed_groups[key] = group.copy()
                renamed_groups[key].name = key
            assert key == renamed_groups[key].name
        msg = [value.to_bytes() for value in renamed_groups.values()]
        return srsly.msgpack_dumps(msg)

    def from_bytes(self, bytes_data: bytes) -> "SpanGroups":
        # backwards-compatibility: bytes_data may be one of:
        # b'', a serialized empty list, or a serialized list of SpanGroup bytes
        msg = (
            []
            if not bytes_data or bytes_data == self._EMPTY_BYTES
            else srsly.msgpack_loads(bytes_data)
        )
        self.clear()
        doc = self._ensure_doc()
        for value_bytes in msg:
            group = SpanGroup(doc).from_bytes(value_bytes)
            if group.name in self:
                # Display a warning if `msg` contains `SpanGroup`s
                # that have the same .name (attribute).
                # Because, for `SpanGroups` serialized as lists,
                # only 1 SpanGroup per .name is loaded. (See #10685)
                warnings.warn(
                    Warnings.W119.format(group_name=group.name, group_values=group)
                )
                continue
            self[group.name] = group
        return self

    def _ensure_doc(self) -> "Doc":
        doc = self.doc_ref()
        if doc is None:
            raise ValueError(Errors.E866)
        return doc
