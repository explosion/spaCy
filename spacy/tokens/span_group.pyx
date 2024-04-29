# cython: profile=False
import struct
import weakref
from copy import deepcopy
from typing import Iterable, Optional, Union

import srsly

from spacy.errors import Errors

from .span cimport Span


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
            spans=[doc[0:1], doc[1:3]],
            attrs={"annotator": "matt"}
        )

        Construction 2
        >>> doc = nlp("Their goi ng home")
        >>> doc.spans["errors"] = [doc[0:1], doc[1:3]]
        >>> assert isinstance(doc.spans["errors"], SpanGroup)

    DOCS: https://spacy.io/api/spangroup
    """
    def __init__(self, doc, *, name="", attrs={}, spans=[]):  # no-cython-lint
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
        if len(spans) :
            self.c.reserve(len(spans))
        for span in spans:
            if doc is not span.doc:
                raise ValueError(Errors.E855.format(obj="span"))
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

    def __getitem__(self, int i) -> Span:
        """Get a span from the group. Note that a copy of the span is returned,
        so if any changes are made to this span, they are not reflected in the
        corresponding member of the span group.

        i (int): The item index.
        RETURNS (Span): The span at the given index.

        DOCS: https://spacy.io/api/spangroup#getitem
        """
        i = self._normalize_index(i)
        return Span.cinit(self.doc, self.c[i])

    def __delitem__(self, int i):
        """Delete a span from the span group at index i.

        i (int): The item index.

        DOCS: https://spacy.io/api/spangroup#delitem
        """
        i = self._normalize_index(i)
        self.c.erase(self.c.begin() + i - 1)

    def __setitem__(self, int i, Span span):
        """Set a span in the span group.

        i (int): The item index.
        span (Span): The span.

        DOCS: https://spacy.io/api/spangroup#setitem
        """
        if span.doc is not self.doc:
            raise ValueError(Errors.E855.format(obj="span"))

        i = self._normalize_index(i)
        self.c[i] = span.c

    def __iadd__(self, other: Union[SpanGroup, Iterable["Span"]]) -> SpanGroup:
        """Operator +=. Append a span group or spans to this group and return
        the current span group.

        other (Union[SpanGroup, Iterable["Span"]]): The SpanGroup or spans to
            add.

        RETURNS (SpanGroup): The current span group.

        DOCS: https://spacy.io/api/spangroup#iadd
        """
        return self._concat(other, inplace=True)

    def __add__(self, other: SpanGroup) -> SpanGroup:
        """Operator +. Concatenate a span group with this group and return a
        new span group.

        other (SpanGroup): The SpanGroup to add.

        RETURNS (SpanGroup): The concatenated SpanGroup.

        DOCS: https://spacy.io/api/spangroup#add
        """
        # For Cython 0.x and __add__, you cannot rely on `self` as being `self`
        # or being the right type, so both types need to be checked explicitly.
        if isinstance(self, SpanGroup) and isinstance(other, SpanGroup):
            return self._concat(other)
        return NotImplemented

    def __iter__(self):
        """
        Iterate over the spans in this SpanGroup.
        YIELDS (Span): A span in this SpanGroup.

        DOCS: https://spacy.io/api/spangroup#iter
        """
        for i in range(self.c.size()):
            yield self[i]

    def append(self, Span span):
        """Add a span to the group. The span must refer to the same Doc
        object as the span group.

        span (Span): The span to append.

        DOCS: https://spacy.io/api/spangroup#append
        """
        if span.doc is not self.doc:
            raise ValueError(Errors.E855.format(obj="span"))
        self.push_back(span.c)

    def extend(self, spans_or_span_group: Union[SpanGroup, Iterable["Span"]]):
        """Add multiple spans or contents of another SpanGroup to the group.
        All spans must refer to the same Doc object as the span group.

        spans (Union[SpanGroup, Iterable["Span"]]): The spans to add.

        DOCS: https://spacy.io/api/spangroup#extend
        """
        self._concat(spans_or_span_group, inplace=True)

    def to_bytes(self):
        """Serialize the SpanGroup's contents to a byte string.

        RETURNS (bytes): The serialized span group.

        DOCS: https://spacy.io/api/spangroup#to_bytes
        """
        output = {"name": self.name, "attrs": self.attrs, "spans": []}
        cdef int i
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

    def copy(self, doc: Optional["Doc"] = None) -> SpanGroup:
        """Clones the span group.

        doc (Doc): New reference document to which the copy is bound.
        RETURNS (SpanGroup): A copy of the span group.

        DOCS: https://spacy.io/api/spangroup#copy
        """
        if doc is None:
            doc = self.doc
        if doc is self.doc:
            spans = list(self)
        else:
            spans = [doc.char_span(span.start_char, span.end_char, label=span.label_, kb_id=span.kb_id, span_id=span.id) for span in self]
            for i, span in enumerate(spans):
                if span is None:
                    raise ValueError(Errors.E1052.format(i=i))
                if span.kb_id in self.doc.vocab.strings:
                    doc.vocab.strings.add(span.kb_id_)
                if span.id in span.doc.vocab.strings:
                    doc.vocab.strings.add(span.id_)
        return SpanGroup(
            doc,
            name=self.name,
            attrs=deepcopy(self.attrs),
            spans=spans,
        )

    def _concat(
        self,
        other: Union[SpanGroup, Iterable["Span"]],
        *,
        inplace: bool = False,
    ) -> SpanGroup:
        """Concatenates the current span group with the provided span group or
        spans, either in place or creating a copy. Preserves the name of self,
        updates attrs only with values that are not in self.

        other (Union[SpanGroup, Iterable[Span]]): The spans to append.
        inplace (bool): Indicates whether the operation should be performed in
            place on the current span group.

        RETURNS (SpanGroup): Either a new SpanGroup or the current SpanGroup
        depending on the value of inplace.
        """
        cdef SpanGroup span_group = self if inplace else self.copy()
        cdef SpanGroup other_group
        cdef Span span

        if isinstance(other, SpanGroup):
            other_group = other
            if other_group.doc is not self.doc:
                raise ValueError(Errors.E855.format(obj="span group"))

            other_attrs = deepcopy(other_group.attrs)
            span_group.attrs.update({
                key: value for key, value in other_attrs.items()
                if key not in span_group.attrs
            })
            if len(other_group):
                span_group.c.reserve(span_group.c.size() + other_group.c.size())
                span_group.c.insert(span_group.c.end(), other_group.c.begin(), other_group.c.end())
        else:
            if len(other):
                span_group.c.reserve(self.c.size() + len(other))
            for span in other:
                if span.doc is not self.doc:
                    raise ValueError(Errors.E855.format(obj="span"))
                span_group.c.push_back(span.c)

        return span_group

    def _normalize_index(self, int i) -> int:
        """Checks list index boundaries and adjusts the index if negative.

        i (int): The index.
        RETURNS (int): The adjusted index.
        """
        cdef int length = self.c.size()
        if i < -length or i >= length:
            raise IndexError(Errors.E856.format(i=i, length=length))
        if i < 0:
            i += length
        return i
