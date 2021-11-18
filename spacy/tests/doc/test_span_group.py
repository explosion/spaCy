import pytest
from random import Random
from spacy.matcher import Matcher
from spacy.tokens import Span, SpanGroup
from ..util import assert_span_list_equal, assert_span_list_not_equal
from spacy.util import filter_spans

@pytest.fixture
def doc(en_tokenizer):
    doc = en_tokenizer('0 1 2 3 4 5 6')
    matcher = Matcher(en_tokenizer.vocab, validate=True)

    matcher.add('4', [[{}, {}, {}, {}]])
    matcher.add('2', [[{}, {}, ]])
    matcher.add('1', [[{}, ]])

    matches = matcher(doc)
    spans = []
    for match in matches:
        spans.append(Span(doc, match[1], match[2], en_tokenizer.vocab.strings[match[0]]))
    Random(42).shuffle(spans)
    doc.spans['SPANS'] = SpanGroup(doc, name = 'SPANS', attrs = {'key' : 'value'}, spans = spans)
    return doc

## TODO: DELETE THIS
@pytest.fixture
def span_group(en_tokenizer) :
    doc = en_tokenizer('0 1 2 3 4 5 6')
    matcher = Matcher(en_tokenizer.vocab, validate=True)

    matcher.add('4', [[{}, {}, {}, {}]])
    matcher.add('2', [[{}, {}, ]])
    matcher.add('1', [[{}, ]])

    matches = matcher(doc)
    spans = []
    for match in matches:
        spans.append(Span(doc, match[1], match[2], en_tokenizer.vocab.strings[match[0]]))
    Random(42).shuffle(spans)
    return SpanGroup(doc, name = 'SPANS', attrs = {'key' : 'value'}, spans = spans)

#@pytest.fixture(autouse=True)
#def assert_span_list_equal(spans_1, spans_2) :
#    for span_1, span_2 in zip(spans_1, spans_2) :
#        assert span_1 == span_2

def test_span_group_clone(doc) :
    span_group = doc.spans['SPANS']
    clone = span_group.clone()
    assert clone != span_group
    assert clone.name == span_group.name
    assert clone.attrs == span_group.attrs
    assert len(clone) == len(span_group)
    for original_span, clone_span in zip(span_group, clone) :
        assert original_span == clone_span
    pass

def test_span_group_sort(doc) :
    sorted_spans_expected = [(0, 1), (0, 2), (0, 4), (1, 2), (1, 3), (1, 5), (2, 3), (2, 4), (2, 6), (3, 4), (3, 5), (3, 7), (4, 5), (4, 6), (5, 6), (5, 7), (6, 7)]
    sorted_longest_first_expected = [(0, 4), (0, 2), (0, 1), (1, 5), (1, 3), (1, 2), (2, 6), (2, 4), (2, 3), (3, 7), (3, 5), (3, 4), (4, 6), (4, 5), (5, 7), (5, 6), (6, 7)]

    # Expected spans have label == len(span)
    sorted_spans_expected = [Span(doc, pair[0], pair[1], str(pair[1] - pair[0])) for pair in sorted_spans_expected]
    sorted_longest_first_expected = [Span(doc, pair[0], pair[1], str(pair[1] - pair[0])) for pair in sorted_longest_first_expected]

    span_group = doc.spans['SPANS']
    spans_unsorted = list(span_group)

    ################################################################
    # Test with regular sort order and inplace = False (default)
    ################################################################
    clone = span_group.sort()
    assert clone != span_group
    assert len(clone) == len(span_group)
    assert_span_list_equal(spans_unsorted, span_group)
    assert_span_list_not_equal(span_group, clone)

    assert_span_list_equal(clone, sorted_spans_expected)

    ################################################################
    # Test with longest_first and inplace = False
    ################################################################

    clone = span_group.sort(longest_first = True)
    assert clone != span_group
    assert len(clone) == len(span_group)
    assert_span_list_equal(spans_unsorted, span_group)
    assert_span_list_not_equal(span_group, clone)

    # Now, check that spans were sorted correctly
    assert_span_list_equal(clone, sorted_longest_first_expected)

    ################################################################
    # Test with regular sort order and inplace = True
    ################################################################
    clone = span_group.sort(inplace = True)
    assert clone == span_group
    assert len(clone) == len(span_group)
    assert_span_list_not_equal(spans_unsorted, span_group)

    assert_span_list_equal(clone, sorted_spans_expected)

    pass


def test_span_group_filter_spans(doc) :
    span_group = doc.spans['SPANS']
    spans_unfiltered = list(span_group)
    spans_filtered_expected =  [(0, 4), (4, 6), (6, 7)]
    spans_filtered_expected = [Span(doc, pair[0], pair[1], str(pair[1] - pair[0])) for pair in spans_filtered_expected]

    ################################################################
    # Test with inplace = False (default)
    ################################################################
    clone = span_group.filter_spans()
    assert clone != span_group
    assert len(clone) != len(span_group)
    assert len(clone) == 3
    assert_span_list_equal(spans_unfiltered, span_group)
    assert_span_list_not_equal(span_group, clone)

    assert_span_list_equal(spans_filtered_expected, clone)

    ################################################################
    # Test with inplace = True
    ################################################################
    clone = span_group.filter_spans(inplace = True)
    assert clone == span_group
    assert len(clone) == len(span_group)
    assert len(clone) == 3
    assert_span_list_not_equal(spans_unfiltered, span_group)
    assert_span_list_equal(span_group, clone)

    assert_span_list_equal( spans_filtered_expected, clone)

def test_span_group_get_overlaps(doc) :
    span_group = doc.spans['SPANS']
    spans_original = list(span_group)

    overlaps_partial_expected = [(0, 4), (1, 5), (2, 4), (2, 6), (3, 4), (3, 7), (4, 5), (4, 6)]
    overlaps_no_partial_expected =[(1, 5), (2, 6), (3, 7)]
    overlaps_partial_include_self_expected = [(0, 4), (1, 5), (2, 4), (2, 6), (3, 4), (3, 5), (3, 7), (4, 5), (4, 6)]
    overlaps_no_partial_include_self_expected =  [(1, 5), (2, 6), (3, 5), (3, 7)]

    overlaps_partial_expected = [Span(doc, pair[0], pair[1], str(pair[1] - pair[0])) for pair in overlaps_partial_expected]
    overlaps_no_partial_expected = [Span(doc, pair[0], pair[1], str(pair[1] - pair[0])) for pair in overlaps_no_partial_expected]
    overlaps_partial_include_self_expected = [Span(doc, pair[0], pair[1], str(pair[1] - pair[0])) for pair in overlaps_partial_include_self_expected]
    overlaps_no_partial_include_self_expected = [Span(doc, pair[0], pair[1], str(pair[1] - pair[0])) for pair in overlaps_no_partial_include_self_expected]

    span = Span(doc, 3, 5, '2')

    ################################################################
    # Test with exclude_self = True, exclude_partial = False (default)
    ################################################################
    overlaps = span_group.get_overlaps(span)
    assert overlaps != span_group
    assert len(overlaps) == len(overlaps_partial_expected)
    assert_span_list_equal(overlaps, overlaps_partial_expected)
    assert_span_list_equal(span_group, spans_original)

    ################################################################
    # Test with exclude_self = True, exclude_partial = True
    ################################################################
    overlaps = span_group.get_overlaps(span, exclude_partial = True)
    assert overlaps != span_group
    assert len(overlaps) == len(overlaps_no_partial_expected)
    assert_span_list_equal(overlaps, overlaps_no_partial_expected)
    assert_span_list_equal(span_group, spans_original)

    ################################################################
    # Test with exclude_self = False, exclude_partial = False
    ################################################################
    overlaps = span_group.get_overlaps(span, exclude_self = False, exclude_partial = False)
    assert overlaps != span_group
    assert len(overlaps) == len(overlaps_partial_include_self_expected)
    assert_span_list_equal(overlaps, overlaps_partial_include_self_expected)
    assert_span_list_equal(span_group, spans_original)


    ################################################################
    # Test with exclude_self = False, exclude_partial = True
    ################################################################
    overlaps = span_group.get_overlaps(span, exclude_self = False, exclude_partial = True)
    assert overlaps != span_group
    assert len(overlaps) == len(overlaps_no_partial_include_self_expected)
    assert_span_list_equal(overlaps, overlaps_no_partial_include_self_expected)
    assert_span_list_equal(span_group, spans_original)

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
    assert_span_list_equal(overlaps, overlaps_no_partial_expected)
    assert_span_list_equal(span_group, spans_original)


def test_span_group_set_item(doc) :
    span_group = doc.spans['SPANS']

    index = 5
    span = span_group[index]
    span.label_ = 'NEW LABEL'
    span.kb_id = doc.vocab.strings['KB_ID']

    span_group[index] = span
    assert span_group[index].start == span.start
    assert span_group[index].end == span.end
    assert span_group[index].label == span.label
    assert span_group[index].kb_id == span.kb_id
    assert span_group[index] == span

    with pytest.raises(IndexError) :
        span_group[-100] = span
    with pytest.raises(IndexError):
        span_group[100] = span
