import pytest

from spacy.tokens import Span, SpanGroup
from spacy.tokens._dict_proxies import SpanGroups


@pytest.mark.issue(10685)
def test_issue10685(en_tokenizer):
    """Test `SpanGroups` de/serialization"""
    # Start with a Doc with no SpanGroups
    doc = en_tokenizer("Will it blend?")

    # Test empty `SpanGroups` de/serialization:
    assert len(doc.spans) == 0
    doc.spans.from_bytes(doc.spans.to_bytes())
    assert len(doc.spans) == 0

    # Test non-empty `SpanGroups` de/serialization:
    doc.spans["test"] = SpanGroup(doc, name="test", spans=[doc[0:1]])
    doc.spans["test2"] = SpanGroup(doc, name="test", spans=[doc[1:2]])

    def assert_spangroups():
        assert len(doc.spans) == 2
        assert doc.spans["test"].name == "test"
        assert doc.spans["test2"].name == "test"
        assert list(doc.spans["test"]) == [doc[0:1]]
        assert list(doc.spans["test2"]) == [doc[1:2]]

    # Sanity check the currently-expected behavior
    assert_spangroups()

    # Now test serialization/deserialization:
    doc.spans.from_bytes(doc.spans.to_bytes())

    assert_spangroups()


def test_span_groups_serialization_mismatches(en_tokenizer):
    """Test the serialization of multiple mismatching `SpanGroups` keys and `SpanGroup.name`s"""
    doc = en_tokenizer("How now, brown cow?")
    # Some variety:
    # 1 SpanGroup where its name matches its key
    # 2 SpanGroups that have the same name--which is not a key
    # 2 SpanGroups that have the same name--which is a key
    # 1 SpanGroup that is a value for 2 different keys (where its name is a key)
    # 1 SpanGroup that is a value for 2 different keys (where its name is not a key)
    groups = doc.spans
    groups["key1"] = SpanGroup(doc, name="key1", spans=[doc[0:1], doc[1:2]])
    groups["key2"] = SpanGroup(doc, name="too", spans=[doc[3:4], doc[4:5]])
    groups["key3"] = SpanGroup(doc, name="too", spans=[doc[1:2], doc[0:1]])
    groups["key4"] = SpanGroup(doc, name="key4", spans=[doc[0:1]])
    groups["key5"] = SpanGroup(doc, name="key4", spans=[doc[0:1]])
    sg6 = SpanGroup(doc, name="key6", spans=[doc[0:1]])
    groups["key6"] = sg6
    groups["key7"] = sg6
    sg8 = SpanGroup(doc, name="also", spans=[doc[1:2]])
    groups["key8"] = sg8
    groups["key9"] = sg8

    regroups = SpanGroups(doc).from_bytes(groups.to_bytes())

    # Assert regroups == groups
    assert regroups.keys() == groups.keys()
    for key, regroup in regroups.items():
        # Assert regroup == groups[key]
        assert regroup.name == groups[key].name
        assert list(regroup) == list(groups[key])


@pytest.mark.parametrize(
    "spans_bytes,doc_text,expected_spangroups,expected_warning",
    # The bytestrings below were generated from an earlier version of spaCy
    # that serialized `SpanGroups` as a list of SpanGroup bytes (via SpanGroups.to_bytes).
    # Comments preceding the bytestrings indicate from what Doc they were created.
    [
        # Empty SpanGroups:
        (b"\x90", "", {}, False),
        # doc = nlp("Will it blend?")
        # doc.spans['test'] = SpanGroup(doc, name='test', spans=[doc[0:1]])
        (
            b"\x91\xc4C\x83\xa4name\xa4test\xa5attrs\x80\xa5spans\x91\xc4(\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x04",
            "Will it blend?",
            {"test": {"name": "test", "spans": [(0, 1)]}},
            False,
        ),
        # doc = nlp("Will it blend?")
        # doc.spans['test']  = SpanGroup(doc, name='test', spans=[doc[0:1]])
        # doc.spans['test2'] = SpanGroup(doc, name='test', spans=[doc[1:2]])
        (
            b"\x92\xc4C\x83\xa4name\xa4test\xa5attrs\x80\xa5spans\x91\xc4(\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x04\xc4C\x83\xa4name\xa4test\xa5attrs\x80\xa5spans\x91\xc4(\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x05\x00\x00\x00\x07",
            "Will it blend?",
            # We expect only 1 SpanGroup to be in doc.spans in this example
            # because there are 2 `SpanGroup`s that have the same .name. See #10685.
            {"test": {"name": "test", "spans": [(1, 2)]}},
            True,
        ),
        # doc = nlp('How now, brown cow?')
        # doc.spans['key1'] = SpanGroup(doc, name='key1', spans=[doc[0:1], doc[1:2]])
        # doc.spans['key2'] = SpanGroup(doc, name='too', spans=[doc[3:4], doc[4:5]])
        # doc.spans['key3'] = SpanGroup(doc, name='too', spans=[doc[1:2], doc[0:1]])
        # doc.spans['key4'] = SpanGroup(doc, name='key4', spans=[doc[0:1]])
        # doc.spans['key5'] = SpanGroup(doc, name='key4', spans=[doc[0:1]])
        (
            b"\x95\xc4m\x83\xa4name\xa4key1\xa5attrs\x80\xa5spans\x92\xc4(\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x03\xc4(\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x04\x00\x00\x00\x07\xc4l\x83\xa4name\xa3too\xa5attrs\x80\xa5spans\x92\xc4(\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x04\x00\x00\x00\t\x00\x00\x00\x0e\xc4(\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00\x05\x00\x00\x00\x0f\x00\x00\x00\x12\xc4l\x83\xa4name\xa3too\xa5attrs\x80\xa5spans\x92\xc4(\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x04\x00\x00\x00\x07\xc4(\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x03\xc4C\x83\xa4name\xa4key4\xa5attrs\x80\xa5spans\x91\xc4(\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x03\xc4C\x83\xa4name\xa4key4\xa5attrs\x80\xa5spans\x91\xc4(\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x03",
            "How now, brown cow?",
            {
                "key1": {"name": "key1", "spans": [(0, 1), (1, 2)]},
                "too": {"name": "too", "spans": [(1, 2), (0, 1)]},
                "key4": {"name": "key4", "spans": [(0, 1)]},
            },
            True,
        ),
    ],
)
def test_deserialize_span_groups_compat(
    en_tokenizer, spans_bytes, doc_text, expected_spangroups, expected_warning
):
    """Test backwards-compatibility of `SpanGroups` deserialization.
    This uses serializations (bytes) from a prior version of spaCy (before 3.3.1).

    spans_bytes (bytes): Serialized `SpanGroups` object.
    doc_text (str): Doc text.
    expected_spangroups (dict):
        Dict mapping every expected (after deserialization) `SpanGroups` key
        to a SpanGroup's "args", where a SpanGroup's args are given as a dict:
          {"name": span_group.name,
           "spans": [(span0.start, span0.end), ...]}
    expected_warning (bool): Whether a warning is to be expected from .from_bytes()
        --i.e. if more than 1 SpanGroup has the same .name within the `SpanGroups`.
    """
    doc = en_tokenizer(doc_text)

    if expected_warning:
        with pytest.warns(UserWarning):
            doc.spans.from_bytes(spans_bytes)
    else:
        # TODO: explicitly check for lack of a warning
        doc.spans.from_bytes(spans_bytes)

    assert doc.spans.keys() == expected_spangroups.keys()
    for name, spangroup_args in expected_spangroups.items():
        assert doc.spans[name].name == spangroup_args["name"]
        spans = [Span(doc, start, end) for start, end in spangroup_args["spans"]]
        assert list(doc.spans[name]) == spans


def test_span_groups_serialization(en_tokenizer):
    doc = en_tokenizer("0 1 2 3 4 5 6")
    span_groups = SpanGroups(doc)
    spans = [doc[0:2], doc[1:3]]
    sg1 = SpanGroup(doc, spans=spans)
    span_groups["key1"] = sg1
    span_groups["key2"] = sg1
    span_groups["key3"] = []
    reloaded_span_groups = SpanGroups(doc).from_bytes(span_groups.to_bytes())
    assert span_groups.keys() == reloaded_span_groups.keys()
    for key, value in span_groups.items():
        assert all(
            span == reloaded_span
            for span, reloaded_span in zip(span_groups[key], reloaded_span_groups[key])
        )
