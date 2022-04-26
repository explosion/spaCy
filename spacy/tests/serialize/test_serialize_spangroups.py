import pytest

from spacy.tokens import Span, SpanGroup


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
        assert set(doc.spans["test"]) == {doc[0:1]}
        assert set(doc.spans["test2"]) == {doc[1:2]}

    # Sanity check the currently-expected behavior
    assert_spangroups()

    # Now test serialization/deserialization:
    doc.spans.from_bytes(doc.spans.to_bytes())

    assert_spangroups()


@pytest.mark.parametrize(
    "spans_bytes,expected_spangroups,expected_warning",
    [
        # The following 3 bytestrings were generated from `doc = nlp("Will it blend?")`
        # (via `doc.spans.to_bytes()`) from a version of spaCy that serialized
        # `SpanGroups` as a list of SpanGroup bytes.
        # Empty doc.spans:
        (b"\x90", {}, False),
        # `doc.spans['test']  = SpanGroup(doc, name='test', spans=[doc[0:1]])`:
        (
            b"\x91\xc4C\x83\xa4name\xa4test\xa5attrs\x80\xa5spans\x91\xc4(\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x04",
            {"test": {"name": "test", "spans": [(0, 1)]}},
            False,
        ),
        # `doc.spans['test']  = SpanGroup(doc, name='test', spans=[doc[0:1]])` and
        # `doc.spans['test2'] = SpanGroup(doc, name='test', spans=[doc[1:2]])`:
        # (Note: we expect only 1 SpanGroup to be in doc.spans in the following example
        #  because there are 2 `SpanGroup`s that have the same .name. See #10685.)
        (
            b"\x92\xc4C\x83\xa4name\xa4test\xa5attrs\x80\xa5spans\x91\xc4(\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x04\xc4C\x83\xa4name\xa4test\xa5attrs\x80\xa5spans\x91\xc4(\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x05\x00\x00\x00\x07",
            {"test": {"name": "test", "spans": [(1, 2)]}},
            True,
        ),
    ],
)
def test_deserialize_spangroups_compat(
    en_tokenizer, spans_bytes, expected_spangroups, expected_warning
):
    """Test backwards-compatibility of `SpanGroups` deserialization.
    This uses serializations (bytes) from a prior version of spaCy.

    spans_bytes (bytes): Serialized `SpanGroups` object.
    expected_spangroups (dict):
        Dict mapping every expected (after deserialization) `SpanGroups` key
        to a SpanGroup's "args", where a SpanGroup's args are given as a dict:
          {"name": "${SpanGroup.name}",
           "spans": [(span0_start_token_idx, span0_end_token_idx), ...]}
    expected_warning (bool): Whether a warning is to be expected from .from_bytes()
        --i.e. if more than 1 SpanGroup has the same .name within the `SpanGroups`.
    """
    doc = en_tokenizer("Will it blend?")

    if expected_warning:
        with pytest.warns(UserWarning):
            doc.spans.from_bytes(spans_bytes)
    else:
        doc.spans.from_bytes(spans_bytes)

    assert len(doc.spans) == len(expected_spangroups)
    for name, spangroup_args in expected_spangroups.items():
        assert doc.spans[name].name == spangroup_args["name"]
        spans = {Span(doc, start, end) for start, end in spangroup_args["spans"]}
        assert set(doc.spans[name]) == spans
