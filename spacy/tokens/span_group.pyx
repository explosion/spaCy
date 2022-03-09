from typing import Iterable, Tuple, Union, Optional, TYPE_CHECKING
import weakref
import struct
import srsly

from spacy.errors import Errors
from .span cimport Span
from ..structs cimport SpanC

from libcpp.algorithm cimport sort as sort_vector
from libcpp.set cimport set
from libcpp.utility cimport pair


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
        if len(spans) :
            self.c.reserve(len(spans))
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
        cdef vector[SpanC] sorted_spans = self.c
        _sort_span_c_vector(sorted_spans)
        cdef int last_end = sorted_spans[0].end
        cdef SpanC span
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

    def extend(self, spans_or_span_group : Union[SpanGroup, Iterable["Span"]]):
        """Add multiple spans or contents of another SpanGroup to the group.
           All spans must refer to the same Doc object as the span group.

         spans (Iterable[Span]): The spans to add.

         DOCS: https://spacy.io/api/spangroup#extend
         """
        self.concat(spans_or_span_group, inplace = True)


    def __getitem__(self, int i):
        """Get a span from the group.

        i (int): The item index.
        RETURNS (Span): The span at the given index.

        DOCS: https://spacy.io/api/spangroup#getitem
        """
        i = self._validate_and_adjust_index(i)
        return Span.cinit(self.doc, self.c[i])

    def __delitem__(self, int i) :
        """Delete a span from the group at index i

        i (int): The item index.

        DOCS: https://spacy.io/api/spangroup#delitem
        """
        i = self._validate_and_adjust_index(i)
        self.c.erase(self.c.begin() + i - 1)

    def __setitem__(self, int i, Span span) :
        """Update a span in the group.

        i (int): The item index.
        span (Span) : span

        DOCS: https://spacy.io/api/spangroup#setitem
        """
        if span.doc is not self.doc:
            raise ValueError("Cannot add span to group: refers to different Doc.")

        i = self._validate_and_adjust_index(i)
        self.c[i] = span.c

    def __iadd__(self, other : Union[SpanGroup, Iterable["Span"]]) :
        """ Operator +. Append a SpanGroup or Iterable[Span] to this group and
            return self.

            other (SpanGroup or Iterable["Span"]):SpanGroup or spans to add

            RETURNS (SpanGroup): returns the concatenated SpanGroup

            DOCS: https://spacy.io/api/spangroup#iadd
        """
        self.concat(other, inplace = True)
        return self

    def __add__(self, other : Union[SpanGroup, Iterable["Span"]]):
        """ Operator +. Concatenate a SpanGroup or Iterable[Span] with this group and
        return a new SpanGroup

        other (SpanGroup or Iterable["Span"]):SpanGroup or spans to add

        RETURNS (SpanGroup): returns the concatenated SpanGroup

        DOCS: https://spacy.io/api/spangroup#add
        """
        return self.concat(other)


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

    def sort(self, inplace = False, longest_first = False):
        """
        inplace (bool): Indicates if the operation should be performed inplace
        longest_first (bool) : Indicates if sort should be descending by the span length rather than ascending
        RETURNS (SpanGroup): Either self or a new SpanGroup with sorted spans

        DOCS: https://spacy.io/api/spangroup#sort
        """
        cdef SpanGroup span_group = self if inplace else self.clone()

        _sort_span_c_vector(span_group.c, longest_first)
        return span_group

    def clone(self) :
        """
        Clones SpanGroup (self)

        RETURNS (SpanGroup): A copy of self

        DOCS: https://spacy.io/api/spangroup#clone
        """
        cdef SpanGroup span_group = SpanGroup(self.doc, name=self.name, attrs=dict(self.attrs))
        span_group.c = self.c
        return span_group

    def filter_spans(self, inplace = False):
        """
        Filter a sequence of spans and remove duplicates or overlaps. When spans overlap, the (first)
        longest span is preferred over shorter spans.

        inplace (bool): Indicates if the operation should be performed inplace or on a copy of SpanGroup
        RETURNS (SpanGroup): A either self or a copy of self with filtered spans

        DOCS: https://spacy.io/api/spangroup#filter_spans
        """
        cdef SpanGroup span_group = self if inplace else self.clone()
        span_group.c = _filter_spans(span_group.c)
        return span_group

    def get_overlaps(self, Span span, exclude_self = True, exclude_partial = False) :
        """
        Selects spans from self that are overlapping with the given span. Returns a copy of
        self with selected spans only.

        span (Span):
        exclude_self (bool):
        exclude_partial (bool):

        RETURNS (SpanGroup):

        DOCS: https://spacy.io/api/spangroup#get_overlaps
        """

        if span.doc is not self.doc:
            raise ValueError("Cannot add span to group: refers to different Doc.")

        cdef Span current_span = span
        cdef int start = current_span.start
        cdef int end = current_span.end
        cdef vector[SpanC] spans = self.c
        cdef vector[SpanC] result

        _sort_span_c_vector(spans)

        for candidate in spans:
            if candidate.end <= start:
                continue
            if candidate.start >= end:
                break
            if exclude_partial and (candidate.start > start or candidate.end < end ) :
                continue
            if not exclude_self or not _span_c_equal(candidate, current_span.c):
                result.push_back(candidate)

        cdef SpanGroup span_group = self.clone()
        span_group.c = result
        return span_group

    def concat(self, other : Union[SpanGroup, Iterable["Span"]], sort_spans = False, filter_spans = False, inplace = False) :
        """
        Concatenates given SpanGroup with self, either in place or creating a copy. Optionally sorts and filters spans.
        Preserves the name of self, updates attrs only with values that are not in self.

        other (SpanGroup or Iterable[Span): the group to append to this one
        sort_spans (bool): Indicates if sort should be performed
        filter_spans (bool): Indicates if result spans should be filtered
        inplace (bool): Indicates if the operation should be performed on self

        RETURNS (SpanGroup): either a new SpanGroup or self depending on the value of inplace

        DOCS: https://spacy.io/api/spangroup#concat
        """
        cdef SpanGroup span_group = self if inplace else self.clone()
        cdef SpanGroup other_group
        cdef Span span

        if isinstance(other, SpanGroup) :
            other_group = other
            if other_group.doc is not self.doc:
                raise ValueError("Cannot concat SpanGroup with group: refers to different Doc.")

            span_group.attrs.update({key : value for key, value in other_group.attrs.items() if key not in span_group.attrs })
            if len(other_group) :
                span_group.c.reserve(span_group.c.size() + other_group.c.size())
                span_group.c.insert(span_group.c.end(), other_group.c.begin(), other_group.c.end())
        else :
            spans = other
            if len(spans) :
                span_group.c.reserve(self.c.size() + len(spans))
            for span in spans:
                if span.doc is not self.doc:
                    raise ValueError("Cannot add span to the group: refers to different Doc.")
                span_group.c.push_back(span.c)

        if filter_spans :
            span_group.filter_spans(inplace = True)
        elif sort_spans :
            span_group.sort(inplace = True)
        return span_group

    def _validate_and_adjust_index(self, index):
        """
        Checks list index boundaries and adjusts the index if negative to accommodate python slice conventions.
        Used internally in __setitem__/__getitem__ etc.
        If the index is out of range, IndexError is raised.

        index (int): list index
        RETURNS (int): adjusted index
        """
        cdef int size = self.c.size()
        if index < -size or index >= size:
            raise IndexError(f"list index {index} out of range")
        if index < 0:
            index += size
        return index

def concat_span_groups(span_groups : Iterable[SpanGroup], name = None, attrs = None, sort_spans = False, filter_spans = False) :
    """
    Concatenates a list of SpanGroups into a single SpanGroup.
    span_group (List of SpanGroups):
    name (str): name of the result SpanGroup. If not specified, the mame of the first group will be used
    attrs (dict): attrs of the result SpanGroup. If not specified, merged dictionary of attrs of
                  all span groups will be used (without overwriting the keys that are already in attrs
                  from earlier groups)
    sort_spans (bool): Indicates if the result spans should be sorted
    filter_spans (bool): Indicates if the result spans shuold be filtered

    RETURNS (SpanGroup): either a new SpanGroup or self depending on the value of inplace

    DOCS: https://spacy.io/api/spangroup#concat_span_groups
    """
    cdef SpanGroup new_group = None
    cdef int ii
    cdef SpanGroup group
    cdef int size = 0

    span_groups = list(span_groups)
    if len(span_groups) :
        doc = span_groups[0].doc

        new_group = SpanGroup(span_groups[0].doc)
        new_group.name = span_groups[0].name if name is None else name
        new_group.attrs = dict(span_groups[0].attrs) if attrs is None else attrs

        for group in span_groups :
            size += group.c.size()

        if size :
            new_group.c.reserve(size)

        for group in span_groups :
            if group.doc is not doc:
                raise ValueError("Cannot concat SpanGroups: refer to different Doc.")
            if group.c.size() :
                new_group.c.insert(new_group.c.end(), group.c.begin(), group.c.end())
            if attrs is None :
                # If attrs is not provided, we will merge those from all groups
                new_group.attrs.update({key: value for key, value in group.attrs.items() if key not in new_group.attrs})

        if filter_spans :
            new_group.filter_spans(inplace = True)
        elif sort_spans :
            new_group.sort(inplace = True)
    return new_group

cdef bint _compare_span_c(const SpanC& span_1, const SpanC& span_2) nogil:
    """
    A comparator for std::sort method, allowing to sort by span.start first, and then by span.end
    RETURNS (bint): True if (span_1.start, span_1.end) is less than (span_2.start, span_2.end)
    """
    cdef pair[int, int] pair_1 = pair[int, int](span_1.start, span_1.end)
    cdef pair[int, int] pair_2 = pair[int, int](span_2.start, span_2.end)
    return pair_1 < pair_2

cdef bint _compare_span_c_prefer_longest(const SpanC& span_1, const SpanC& span_2) nogil:
    """
    A Comparator for std::sort method, allowing to sort by span.start first, and then descending by span length
    RETURNS (bint): True if (span_1.start, - 1 * span_1.end) is less than (span_2.start, _1 * span_2.end)
    """
    cdef pair[int, int] pair_1 = pair[int, int](span_1.start, -1 * span_1.end)
    cdef pair[int, int] pair_2 = pair[int, int](span_2.start, -1 * span_2.end)
    return pair_1 < pair_2

cdef void _sort_span_c_vector(vector[SpanC]& vector, bint longest_first = False) nogil :
    """
    Sorts an STL vector of SpanC in place, ordering by span.start (ascending) 
    and then by span.end ascending if longest_first is False and descending otherwise 
    """
    cdef bint (*comparator)(const SpanC &, const SpanC &) nogil

    if longest_first:
        comparator = &_compare_span_c_prefer_longest
    else:
        comparator = &_compare_span_c

    sort_vector(vector.begin(), vector.end(), comparator)


cdef bint _span_c_equal(const SpanC& span_1, const SpanC& span_2) nogil :
    """
    Determines if two SpanC structs are equal (by the same criteria as Span.__richcomp__ does)
    """
    return (# Do not compare id, start, end to be consistent with Span.__richcmp__
            span_1.start_char == span_2.start_char and
            span_1.end_char == span_2.end_char and
            span_1.label == span_2.label and
            span_1.kb_id == span_2.kb_id
            )


cdef vector[SpanC] _filter_spans(const vector[SpanC]& spans) nogil:
    """Filter a sequence of spans and remove duplicates or overlaps. Useful for
    creating named entities (where one token can only be part of one entity) or
    when merging spans with `Retokenizer.merge`. When spans overlap, the (first)
    longest span is preferred over shorter spans.
    
    This function is similar to the one defined in spacy.util.py, but operates on the SpanC level

    spans (vector[SpanC]): The vector of SpanC structs to filter.
    RETURNS (vector[SpanC]): The vector of filtered SpanC structs.
    """
    cdef vector[SpanC] sorted_spans = spans
    #sort_vector(sorted_spans.begin(), sorted_spans.end(), &_compare_span_c_prefer_longest)
    _sort_span_c_vector(sorted_spans, longest_first = True)

    cdef vector[SpanC] result
    cdef set[int] seen_tokens
    cdef int token

    for span in sorted_spans:
        # Check for end - 1 here because boundaries are inclusive
        if seen_tokens.find(span.start) == seen_tokens.end() and seen_tokens.find(span.end - 1) == seen_tokens.end() :
            result.push_back(span)
            for token in range(span.start, span.end) :
                seen_tokens.insert(token)
    _sort_span_c_vector(result)
    return result
