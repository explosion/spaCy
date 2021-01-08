import weakref
from .span cimport Span


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

    def to_json(self):
        output = {"name": self.name, "attrs": self.attrs, "spans": []}
        for i in range(self.c.size()):
            span = self.c[i]
            output["spans"].append(
                {
                    "id": span.id,
                    "kb_id": span.kb_id,
                    "label": span.label,
                    "start": span.start,
                    "end": span.end,
                    "start_char": span.start_char,
                    "end_char": span.end_char,
                }
            )
        return output

    cdef void push_back(self, SpanC span) nogil:
        self.c.push_back(span)
