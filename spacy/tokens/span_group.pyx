import weakref
import struct
import srsly
from .span cimport Span
from libc.stdint cimport uint64_t, uint32_t, int32_t


cdef class SpanGroup:
    """A group of spans that all refer to the same Doc object.

    Span groups can be used to manage various types of annotations. The group
    can be named, and you can attach additional attributes to it.
    """
    def __init__(self, doc, name="", attrs={}, spans=[]):
        # We need to make this a weak reference, so that the Doc object can
        # own the SpanGroup without circular references. We do want to get
        # the Doc though, because otherwise the API gets annoying.
        self._doc_ref = weakref.ref(doc)
        self.name = name
        self.attrs = dict(attrs) if attrs is not None else {}
        cdef Span span
        for i, span in enumerate(spans):
            self.push_back(span.c)

    @property
    def doc(self):
        return self._doc_ref()

    def __len__(self):
        return self.c.size()

    def append(self, Span span):
        self.push_back(span.c)

    def extend(self, spans):
        cdef Span span
        for span in spans:
            self.append(span)

    def __getitem__(self, int i):
        cdef int size = self.c.size()
        if i < -size or i >= size:
            raise IndexError(f"list index {i} out of range")
        if i < 0:
            i += size
        return Span.cinit(self.doc, self.c[i])

    def to_list(self):
        return [self[i] for i in range(len(self))]

    def to_bytes(self):
        output = {"name": self.name, "attrs": self.attrs, "spans": []}
        for i in range(self.c.size()):
            span = self.c[i]
            # The struct.pack here is probably overkill, but it might help if
            # you're saving tonnes of spans, and it doesn't really add any
            # complexity. We do take care to specify little-endian byte order
            # though, to ensure the message can be loaded back on a different
            # arch.
            # Q: uint64_t
            # q: int64_t
            # L: uint32_t
            # l: int32_t
            output["spans"].append(struct.pack(
                ">QQQllll",
                span.id,
                span.kb_id,
                span.label,
                span.start,
                span.end,
                span.start_char,
                span.end_char
            ))
        return srsly.msgpack_dumps(output)

    def from_bytes(self, byte_string):
        msg = srsly.msgpack_loads(byte_string)
        self.name = msg["name"]
        self.attrs = dict(msg["attrs"])
        self.c.clear()
        self.c.reserve(len(msg["spans"]))
        cdef SpanC span
        for span_data in msg["spans"]:
            items = struct.unpack(">QQQllll", span_data)
            span.id = items[0]
            span.kb_id = items[1]
            span.label = items[2]
            span.start = items[3]
            span.end = items[4]
            span.start_char = items[5]
            span.end_char = items[6]
            self.c.push_back(span)
        return self

    cdef void push_back(self, SpanC span) nogil:
        self.c.push_back(span)
