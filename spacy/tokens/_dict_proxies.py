import weakref
from collections import UserDict
import srsly
from .span_group import SpanGroup

# Why inherit from UserDict instead of dict here?
# Well, the 'dict' class doesn't necessarily delegate everything nicely,
# for performance reasons. The UserDict is slower by better behaved.
# See https://treyhunner.com/2019/04/why-you-shouldnt-inherit-from-list-and-dict-in-python/0ww
class SpanGroups(UserDict):
    """A dict-like proxy held by the Doc, to control access to span groups."""
    def __init__(self, doc, items=tuple()):
        self.doc_ref = weakref.ref(doc)
        UserDict.__init__(self, items)

    def __setitem__(self, key, value):
        if not isinstance(value, SpanGroup):
            value = self._make_span_group(key, value)
        assert value.doc is self.doc_ref()
        UserDict.__setitem__(self, key, value)

    def _make_span_group(self, name, spans):
        return SpanGroup(self.doc_ref(), name=name, spans=spans)

    def to_bytes(self):
        # We don't need to serialize this as a dict, because the groups
        # know their names.
        msg = [value.to_bytes() for value in self.values()]
        return srsly.msgpack_dumps(msg)

    def from_bytes(self, bytes_data):
        msg = srsly.msgpack_loads(bytes_data)
        self.clear()
        doc = self.doc_ref()
        for value_bytes in msg:
            group = SpanGroup(doc).from_bytes(value_bytes)
            self[group.name] = group
        return self



