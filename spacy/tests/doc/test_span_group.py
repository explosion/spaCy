import pytest
from random import Random
from spacy.matcher import Matcher
from spacy.tokens import Span, SpanGroup
from ..util import span_lists_equal
from spacy.tokens.span_group import concat_span_groups


@pytest.fixture
def doc(en_tokenizer):
    doc = en_tokenizer("0 1 2 3 4 5 6")
    matcher = Matcher(en_tokenizer.vocab, validate=True)

    matcher.add("4", [[{}, {}, {}, {}]])
    matcher.add(
        "2",
        [
            [
                {},
                {},
            ]
        ],
    )
    matcher.add(
        "1",
        [
            [
                {},
            ]
        ],
    )

    matches = matcher(doc)
    spans = []
    for match in matches:
        spans.append(
            Span(doc, match[1], match[2], en_tokenizer.vocab.strings[match[0]])
        )
    Random(42).shuffle(spans)
    doc.spans["SPANS"] = SpanGroup(
        doc, name="SPANS", attrs={"key": "value"}, spans=spans
    )
    return doc


@pytest.fixture
def other_doc(en_tokenizer):
    doc = en_tokenizer("0 1 2 3 4 5 6")
    matcher = Matcher(en_tokenizer.vocab, validate=True)

    matcher.add("4", [[{}, {}, {}, {}]])
    matcher.add(
        "2",
        [
            [
                {},
                {},
            ]
        ],
    )
    matcher.add(
        "1",
        [
            [
                {},
            ]
        ],
    )

    matches = matcher(doc)
    spans = []
    for match in matches:
        spans.append(
            Span(doc, match[1], match[2], en_tokenizer.vocab.strings[match[0]])
        )
    Random(42).shuffle(spans)
    doc.spans["SPANS"] = SpanGroup(
        doc, name="SPANS", attrs={"key": "value"}, spans=spans
    )
    return doc


@pytest.fixture
def span_group(en_tokenizer):
    doc = en_tokenizer("0 1 2 3 4 5 6")
    matcher = Matcher(en_tokenizer.vocab, validate=True)

    matcher.add("4", [[{}, {}, {}, {}]])
    matcher.add(
        "2",
        [
            [
                {},
                {},
            ]
        ],
    )
    matcher.add(
        "1",
        [
            [
                {},
            ]
        ],
    )

    matches = matcher(doc)
    spans = []
    for match in matches:
        spans.append(
            Span(doc, match[1], match[2], en_tokenizer.vocab.strings[match[0]])
        )
    Random(42).shuffle(spans)
    doc.spans["SPANS"] = SpanGroup(
        doc, name="SPANS", attrs={"key": "value"}, spans=spans
    )


def test_span_group_clone(doc):
    span_group = doc.spans["SPANS"]
    clone = span_group.clone()
    assert clone != span_group
    assert clone.name == span_group.name
    assert clone.attrs == span_group.attrs
    assert len(clone) == len(span_group)
    assert span_lists_equal(span_group, clone)
    clone.name = "new_name"
    clone.attrs["key"] = "new_value"
    clone.append(Span(doc, 0, 6, "LABEL"))
    assert clone.name != span_group.name
    assert clone.attrs != span_group.attrs
    assert span_group.attrs["key"] == "value"
    assert span_lists_equal(span_group, clone) is False
    pass


def test_span_group_sort(doc):
    sorted_spans_expected = [
        (0, 1),
        (0, 2),
        (0, 4),
        (1, 2),
        (1, 3),
        (1, 5),
        (2, 3),
        (2, 4),
        (2, 6),
        (3, 4),
        (3, 5),
        (3, 7),
        (4, 5),
        (4, 6),
        (5, 6),
        (5, 7),
        (6, 7),
    ]
    sorted_longest_first_expected = [
        (0, 4),
        (0, 2),
        (0, 1),
        (1, 5),
        (1, 3),
        (1, 2),
        (2, 6),
        (2, 4),
        (2, 3),
        (3, 7),
        (3, 5),
        (3, 4),
        (4, 6),
        (4, 5),
        (5, 7),
        (5, 6),
        (6, 7),
    ]

    # Expected spans have label == len(span)
    sorted_spans_expected = [
        Span(doc, pair[0], pair[1], str(pair[1] - pair[0]))
        for pair in sorted_spans_expected
    ]
    sorted_longest_first_expected = [
        Span(doc, pair[0], pair[1], str(pair[1] - pair[0]))
        for pair in sorted_longest_first_expected
    ]

    span_group = doc.spans["SPANS"]
    spans_unsorted = list(span_group)

    ################################################################
    # Test with regular sort order and inplace = False (default)
    ################################################################
    clone = span_group.sort()
    assert clone != span_group
    assert len(clone) == len(span_group)
    assert span_lists_equal(spans_unsorted, span_group)
    assert span_lists_equal(span_group, clone) is False

    assert span_lists_equal(clone, sorted_spans_expected)

    ################################################################
    # Test with longest_first and inplace = False
    ################################################################

    clone = span_group.sort(longest_first=True)
    assert clone != span_group
    assert len(clone) == len(span_group)
    assert span_lists_equal(spans_unsorted, span_group)
    assert span_lists_equal(span_group, clone) is False

    # Now, check that spans were sorted correctly
    assert span_lists_equal(clone, sorted_longest_first_expected)

    ################################################################
    # Test with regular sort order and inplace = True
    ################################################################
    clone = span_group.sort(inplace=True)
    assert clone == span_group
    assert len(clone) == len(span_group)
    assert span_lists_equal(spans_unsorted, span_group) is False

    assert span_lists_equal(clone, sorted_spans_expected)

    pass


def test_span_group_filter_spans(doc):
    span_group = doc.spans["SPANS"]
    spans_unfiltered = list(span_group)
    spans_filtered_expected = [(0, 4), (4, 6), (6, 7)]
    spans_filtered_expected = [
        Span(doc, pair[0], pair[1], str(pair[1] - pair[0]))
        for pair in spans_filtered_expected
    ]

    ################################################################
    # Test with inplace = False (default)
    ################################################################
    clone = span_group.filter_spans()
    assert clone != span_group
    assert len(clone) != len(span_group)
    assert len(clone) == 3
    assert span_lists_equal(spans_unfiltered, span_group)
    assert span_lists_equal(span_group, clone) is False

    assert span_lists_equal(spans_filtered_expected, clone)

    ################################################################
    # Test with inplace = True
    ################################################################
    clone = span_group.filter_spans(inplace=True)
    assert clone == span_group
    assert len(clone) == len(span_group)
    assert len(clone) == 3
    assert span_lists_equal(spans_unfiltered, span_group) is False
    assert span_lists_equal(span_group, clone)

    assert span_lists_equal(spans_filtered_expected, clone)


def test_span_group_get_overlaps(doc, other_doc):
    span_group = doc.spans["SPANS"]
    spans_original = list(span_group)

    overlaps_partial_expected = [
        (0, 4),
        (1, 5),
        (2, 4),
        (2, 6),
        (3, 4),
        (3, 7),
        (4, 5),
        (4, 6),
    ]
    overlaps_no_partial_expected = [(1, 5), (2, 6), (3, 7)]
    overlaps_partial_include_self_expected = [
        (0, 4),
        (1, 5),
        (2, 4),
        (2, 6),
        (3, 4),
        (3, 5),
        (3, 7),
        (4, 5),
        (4, 6),
    ]
    overlaps_no_partial_include_self_expected = [(1, 5), (2, 6), (3, 5), (3, 7)]

    overlaps_partial_expected = [
        Span(doc, pair[0], pair[1], str(pair[1] - pair[0]))
        for pair in overlaps_partial_expected
    ]
    overlaps_no_partial_expected = [
        Span(doc, pair[0], pair[1], str(pair[1] - pair[0]))
        for pair in overlaps_no_partial_expected
    ]
    overlaps_partial_include_self_expected = [
        Span(doc, pair[0], pair[1], str(pair[1] - pair[0]))
        for pair in overlaps_partial_include_self_expected
    ]
    overlaps_no_partial_include_self_expected = [
        Span(doc, pair[0], pair[1], str(pair[1] - pair[0]))
        for pair in overlaps_no_partial_include_self_expected
    ]

    span = Span(doc, 3, 5, "2")

    ################################################################
    # Test with exclude_self = True, exclude_partial = False (default)
    ################################################################
    overlaps = span_group.get_overlaps(span)
    assert overlaps != span_group
    assert len(overlaps) == len(overlaps_partial_expected)
    assert span_lists_equal(overlaps, overlaps_partial_expected)
    assert span_lists_equal(span_group, spans_original)

    ################################################################
    # Test with exclude_self = True, exclude_partial = True
    ################################################################
    overlaps = span_group.get_overlaps(span, exclude_partial=True)
    assert overlaps != span_group
    assert len(overlaps) == len(overlaps_no_partial_expected)
    assert span_lists_equal(overlaps, overlaps_no_partial_expected)
    assert span_lists_equal(span_group, spans_original)

    ################################################################
    # Test with exclude_self = False, exclude_partial = False
    ################################################################
    overlaps = span_group.get_overlaps(span, exclude_self=False, exclude_partial=False)
    assert overlaps != span_group
    assert len(overlaps) == len(overlaps_partial_include_self_expected)
    assert span_lists_equal(overlaps, overlaps_partial_include_self_expected)
    assert span_lists_equal(span_group, spans_original)

    ################################################################
    # Test with exclude_self = False, exclude_partial = True
    ################################################################
    overlaps = span_group.get_overlaps(span, exclude_self=False, exclude_partial=True)
    assert overlaps != span_group
    assert len(overlaps) == len(overlaps_no_partial_include_self_expected)
    assert span_lists_equal(overlaps, overlaps_no_partial_include_self_expected)
    assert span_lists_equal(span_group, spans_original)

    ################################################################
    # Test with exclude_self = True, exclude_partial = True
    # but the span with a different label
    # The result will be the same as with eclude_self = False because
    # the span in question is different
    ################################################################
    span.label_ == "ABC"
    overlaps = span_group.get_overlaps(span, exclude_self=True, exclude_partial=True)
    assert overlaps != span_group
    assert len(overlaps) == len(overlaps_no_partial_expected)
    assert span_lists_equal(overlaps, overlaps_no_partial_expected)
    assert span_lists_equal(span_group, spans_original)

    span = Span(other_doc, 3, 5, "2")
    with pytest.raises(ValueError):
        span_group.get_overlaps(span)


def test_span_group_set_item(doc, other_doc):
    span_group = doc.spans["SPANS"]

    index = 5
    span = span_group[index]
    span.label_ = "NEW LABEL"
    span.kb_id = doc.vocab.strings["KB_ID"]

    assert span_group[index].label != span.label
    assert span_group[index].kb_id != span.kb_id

    span_group[index] = span
    assert span_group[index].start == span.start
    assert span_group[index].end == span.end
    assert span_group[index].label == span.label
    assert span_group[index].kb_id == span.kb_id
    assert span_group[index] == span

    with pytest.raises(IndexError):
        span_group[-100] = span
    with pytest.raises(IndexError):
        span_group[100] = span

    span = Span(other_doc, 0, 2)
    with pytest.raises(ValueError):
        span_group[index] = span


def test_span_group_has_overlap(doc):
    span_group = doc.spans["SPANS"]
    assert span_group.has_overlap
    span_group = span_group.filter_spans()
    assert span_group.has_overlap is False


def test_span_group_concat(doc, other_doc):
    span_group_1 = doc.spans["SPANS"]
    spans = [doc[0:5], doc[0:6]]
    span_group_2 = SpanGroup(
        doc,
        name="MORE_SPANS",
        attrs={"key": "new_value", "new_key": "new_value"},
        spans=spans,
    )
    span_group_3 = span_group_1.concat(span_group_2)
    assert span_group_3.name == span_group_1.name
    assert span_group_3.attrs == {"key": "value", "new_key": "new_value"}
    span_list_expected = list(span_group_1) + list(span_group_2)
    assert span_lists_equal(span_group_3, span_list_expected)

    # Filter result spans
    span_group_3 = span_group_1.concat(span_group_2, filter_spans=True)
    span_list_expected = [doc[0:6], Span(doc, 6, 7, "1")]
    assert span_lists_equal(span_group_3, span_list_expected)

    # Sort result spans
    span_list_expected = sorted(
        list(span_group_1) + list(span_group_2), key=lambda x: (x.start, x.end)
    )
    span_group_3 = span_group_1.concat(span_group_2, sort_spans=True)
    assert span_lists_equal(span_group_3, span_list_expected)

    # Inplace
    span_list_expected = list(span_group_1) + list(span_group_2)
    span_group_3 = span_group_1.concat(span_group_2, inplace=True)
    assert span_group_3 == span_group_1
    assert span_group_3.name == span_group_1.name
    assert span_group_3.attrs == {"key": "value", "new_key": "new_value"}
    assert span_lists_equal(span_group_3, span_list_expected)

    span_group_2 = other_doc.spans["SPANS"]
    with pytest.raises(ValueError):
        span_group_1.concat(span_group_2)


def test_span_group_concat_span_groups(doc, other_doc):
    span_list = list(doc.spans["SPANS"])
    n = 3
    span_list = [span_list[i : i + n] for i in range(0, len(span_list), n)]
    span_group_list = []
    for ii, spans in enumerate(span_list):
        attrs = {"key": "value %s" % ii, "key %s" % ii: "value %s" % ii}
        span_group_list.append(
            SpanGroup(doc, name="SpanGroup%d" % ii, attrs=attrs, spans=spans)
        )
    concatenated_group = concat_span_groups(span_group_list)

    expected_list = list(doc.spans["SPANS"])
    expected_attrs = {"key": "value 0"}
    for ii in range(len(span_group_list)):
        expected_attrs["key %s" % ii] = "value %s" % ii
    assert len(concatenated_group) == len(expected_list)
    assert concatenated_group.name == span_group_list[0].name
    assert concatenated_group.attrs == expected_attrs
    assert span_lists_equal(expected_list, concatenated_group)

    expected_list = sorted(list(doc.spans["SPANS"]), key=lambda x: (x.start, x.end))
    concatenated_group = concat_span_groups(
        span_group_list, name="merged", attrs={}, sort_spans=True
    )
    assert concatenated_group.name == "merged"
    assert concatenated_group.attrs == {}
    assert span_lists_equal(expected_list, concatenated_group)

    expected_list = doc.spans["SPANS"].filter_spans()
    concatenated_group = concat_span_groups(
        span_group_list, name="merged", attrs={}, sort_spans=True, filter_spans=True
    )
    assert concatenated_group.name == "merged"
    assert concatenated_group.attrs == {}
    assert span_lists_equal(expected_list, concatenated_group)

    concatenated_group = concat_span_groups(doc.spans.values())
    assert concatenated_group.name == "SPANS"

    span_groups = [x for x in doc.spans.values()] + [
        x for x in other_doc.spans.values()
    ]
    with pytest.raises(ValueError):
        concat_span_groups(span_groups)


def test_span_doc_delitem(doc):
    span_group = doc.spans["SPANS"]
    length = len(span_group)
    index = 5
    span = span_group[index]
    next_span = span_group[index + 1]
    del span_group[index]
    assert len(span_group) == length - 1
    assert span_group[index] != span
    assert span_group[index] == next_span

    with pytest.raises(IndexError):
        del span_group[-100]
    with pytest.raises(IndexError):
        del span_group[100]


def test_span_group_add(doc):
    span_group_1 = doc.spans["SPANS"]
    spans = [doc[0:5], doc[0:6]]
    span_group_2 = SpanGroup(
        doc,
        name="MORE_SPANS",
        attrs={"key": "new_value", "new_key": "new_value"},
        spans=spans,
    )

    span_group_3_expected = span_group_1.concat(span_group_2)

    span_group_3 = span_group_1 + span_group_2
    assert len(span_group_3) == len(span_group_3_expected)
    assert span_group_3.attrs == {"key": "value", "new_key": "new_value"}
    assert span_lists_equal(span_group_3, span_group_3_expected)

    span_group_3 = span_group_1 + spans
    assert len(span_group_3) == len(span_group_3_expected)
    assert span_group_3.attrs == {"key": "value"}
    assert span_lists_equal(span_group_3, span_group_3_expected)


def test_span_group_iadd(doc):
    span_group_1 = doc.spans["SPANS"].clone()
    spans = [doc[0:5], doc[0:6]]
    span_group_2 = SpanGroup(
        doc,
        name="MORE_SPANS",
        attrs={"key": "new_value", "new_key": "new_value"},
        spans=spans,
    )

    span_group_1_expected = span_group_1.concat(span_group_2)

    span_group_1 += span_group_2
    assert len(span_group_1) == len(span_group_1_expected)
    assert span_group_1.attrs == {"key": "value", "new_key": "new_value"}
    assert span_lists_equal(span_group_1, span_group_1_expected)

    span_group_1 = doc.spans["SPANS"].clone()
    span_group_1 += spans
    assert len(span_group_1) == len(span_group_1_expected)
    assert span_group_1.attrs == {
        "key": "value",
    }
    assert span_lists_equal(span_group_1, span_group_1_expected)


def test_span_group_extend(doc):
    span_group_1 = doc.spans["SPANS"].clone()
    spans = [doc[0:5], doc[0:6]]
    span_group_2 = SpanGroup(
        doc,
        name="MORE_SPANS",
        attrs={"key": "new_value", "new_key": "new_value"},
        spans=spans,
    )

    span_group_1_expected = span_group_1.concat(span_group_2)

    span_group_1.extend(span_group_2)
    assert len(span_group_1) == len(span_group_1_expected)
    assert span_group_1.attrs == {"key": "value", "new_key": "new_value"}
    assert span_lists_equal(span_group_1, span_group_1_expected)

    span_group_1 = doc.spans["SPANS"]
    span_group_1.extend(spans)
    assert len(span_group_1) == len(span_group_1_expected)
    assert span_group_1.attrs == {"key": "value"}
    assert span_lists_equal(span_group_1, span_group_1_expected)


def test_span_group_dealloc(span_group):
    with pytest.raises(AttributeError):
        print(span_group.doc)
