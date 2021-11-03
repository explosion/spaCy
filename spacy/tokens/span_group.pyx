import weakref
import struct
import srsly

from spacy.errors import Errors
from .span cimport Span
from libc.stdint cimport uint64_t, uint32_t, int32_t


cdef class SpanGroup:
    """A group of spans that all belong to the same Doc object. The group
    can be named, and you can attach additional attributes to it. Span groups
    are generally accessed via the `doc.spans` attribute. The `doc.spans`
    attribute will convert lists of spans into a `SpanGroup` object for you
    automatically on assignment.

    Example:
        Construction 1
        >>> doc = nlp("Their goi ng home")
        >>> doc.spans["errors"] = SpanGroup(
            doc,
            name="errors",
            spans=[doc[0:1], doc[2:4]],
            attrs={"annotator": "matt"}
        )

        Construction 2
        >>> doc = nlp("Their goi ng home")
        >>> doc.spans["errors"] = [doc[0:1], doc[2:4]]
        >>> assert isinstance(doc.spans["errors"], SpanGroup)

    DOCS: https://spacy.io/api/spangroup
    """
    def __init__(self, doc, *, name="", attrs={}, spans=[]):
        """Create a SpanGroup.

        doc (Doc): The reference Doc object.
        name (str): The group name.
        attrs (Dict[str, Any]): Optional JSON-serializable attributes to attach.
        spans (Iterable[Span]): The spans to add to the group.

        DOCS: https://spacy.io/api/spangroup#init
        """
        # We need to make this a weak reference, so that the Doc object can
        # own the SpanGroup without circular references. We do want to get
        # the Doc though, because otherwise the API gets annoying.
        self._doc_ref = weakref.ref(doc)
        self.name = name
        self.attrs = dict(attrs) if attrs is not None else {}
        cdef Span span
        for span in spans:
            self.push_back(span.c)

    def __repr__(self):
        return str(list(self))

    @property
    def doc(self):
        """RETURNS (Doc): The reference document.

        DOCS: https://spacy.io/api/spangroup#doc
        """
        doc = self._doc_ref()
        if doc is None:
            # referent has been garbage collected
            raise RuntimeError(Errors.E865)
        return doc

    @property
    def has_overlap(self):
        """RETURNS (bool): Whether the group contains overlapping spans.

        DOCS: https://spacy.io/api/spangroup#has_overlap
        """
        if not len(self):
            return False
        sorted_spans = list(sorted(self))
        last_end = sorted_spans[0].end
        for span in sorted_spans[1:]:
            if span.start < last_end:
                return True
            last_end = span.end
        return False

    def __len__(self):
        """RETURNS (int): The number of spans in the group.

        DOCS: https://spacy.io/api/spangroup#len
        """
        return self.c.size()

    def append(self, Span span):
        """Add a span to the group. The span must refer to the same Doc
        object as the span group.

        span (Span): The span to append.

        DOCS: https://spacy.io/api/spangroup#append
        """
        if span.doc is not self.doc:
            raise ValueError("Cannot add span to group: refers to different Doc.")
        self.push_back(span.c)

    def extend(self, spans):
        """Add multiple spans to the group. All spans must refer to the same
        Doc object as the span group.

        spans (Iterable[Span]): The spans to add.

        DOCS: https://spacy.io/api/spangroup#extend
        """
        cdef Span span
        for span in spans:
            self.append(span)

    def __getitem__(self, int i):
        """Get a span from the group.

        i (int): The item index.
        RETURNS (Span): The span at the given index.

        DOCS: https://spacy.io/api/spangroup#getitem
        """
        cdef int size = self.c.size()
        if i < -size or i >= size:
            raise IndexError(f"list index {i} out of range")
        if i < 0:
            i += size
        return Span.cinit(self.doc, self.c[i])

    def to_bytes(self):
        """Serialize the SpanGroup's contents to a byte string.

        RETURNS (bytes): The serialized span group.

        DOCS: https://spacy.io/api/spangroup#to_bytes
        """
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

    def from_bytes(self, bytes_data):
        """Deserialize the SpanGroup's contents from a byte string.

        bytes_data (bytes): The span group to load.
        RETURNS (SpanGroup): The deserialized span group.

        DOCS: https://spacy.io/api/spangroup#from_bytes
        """
        msg = srsly.msgpack_loads(bytes_data)
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
