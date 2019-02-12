# coding: utf-8
from __future__ import unicode_literals

import pytest
from spacy.matcher import PhraseMatcher
from spacy.tokens import Doc
from ..util import get_doc


def test_matcher_phrase_matcher(en_vocab):
    doc = Doc(en_vocab, words=["Google", "Now"])
    matcher = PhraseMatcher(en_vocab)
    matcher.add("COMPANY", None, doc)
    doc = Doc(en_vocab, words=["I", "like", "Google", "Now", "best"])
    assert len(matcher(doc)) == 1


def test_phrase_matcher_length(en_vocab):
    matcher = PhraseMatcher(en_vocab)
    assert len(matcher) == 0
    matcher.add("TEST", None, Doc(en_vocab, words=["test"]))
    assert len(matcher) == 1
    matcher.add("TEST2", None, Doc(en_vocab, words=["test2"]))
    assert len(matcher) == 2


def test_phrase_matcher_contains(en_vocab):
    matcher = PhraseMatcher(en_vocab)
    matcher.add("TEST", None, Doc(en_vocab, words=["test"]))
    assert "TEST" in matcher
    assert "TEST2" not in matcher


def test_phrase_matcher_string_attrs(en_vocab):
    words1 = ["I", "like", "cats"]
    pos1 = ["PRON", "VERB", "NOUN"]
    words2 = ["Yes", ",", "you", "hate", "dogs", "very", "much"]
    pos2 = ["INTJ", "PUNCT", "PRON", "VERB", "NOUN", "ADV", "ADV"]
    pattern = get_doc(en_vocab, words=words1, pos=pos1)
    matcher = PhraseMatcher(en_vocab, attr="POS")
    matcher.add("TEST", None, pattern)
    doc = get_doc(en_vocab, words=words2, pos=pos2)
    matches = matcher(doc)
    assert len(matches) == 1
    match_id, start, end = matches[0]
    assert match_id == en_vocab.strings["TEST"]
    assert start == 2
    assert end == 5


def test_phrase_matcher_string_attrs_negative(en_vocab):
    """Test that token with the control codes as ORTH are *not* matched."""
    words1 = ["I", "like", "cats"]
    pos1 = ["PRON", "VERB", "NOUN"]
    words2 = ["matcher:POS-PRON", "matcher:POS-VERB", "matcher:POS-NOUN"]
    pos2 = ["X", "X", "X"]
    pattern = get_doc(en_vocab, words=words1, pos=pos1)
    matcher = PhraseMatcher(en_vocab, attr="POS")
    matcher.add("TEST", None, pattern)
    doc = get_doc(en_vocab, words=words2, pos=pos2)
    matches = matcher(doc)
    assert len(matches) == 0


def test_phrase_matcher_bool_attrs(en_vocab):
    words1 = ["Hello", "world", "!"]
    words2 = ["No", "problem", ",", "he", "said", "."]
    pattern = Doc(en_vocab, words=words1)
    matcher = PhraseMatcher(en_vocab, attr="IS_PUNCT")
    matcher.add("TEST", None, pattern)
    doc = Doc(en_vocab, words=words2)
    matches = matcher(doc)
    assert len(matches) == 2
    match_id1, start1, end1 = matches[0]
    match_id2, start2, end2 = matches[1]
    assert match_id1 == en_vocab.strings["TEST"]
    assert match_id2 == en_vocab.strings["TEST"]
    assert start1 == 0
    assert end1 == 3
    assert start2 == 3
    assert end2 == 6


def test_phrase_matcher_validation(en_vocab):
    doc1 = Doc(en_vocab, words=["Test"])
    doc1.is_parsed = True
    doc2 = Doc(en_vocab, words=["Test"])
    doc2.is_tagged = True
    doc3 = Doc(en_vocab, words=["Test"])
    matcher = PhraseMatcher(en_vocab, validate=True)
    with pytest.warns(UserWarning):
        matcher.add("TEST1", None, doc1)
    with pytest.warns(UserWarning):
        matcher.add("TEST2", None, doc2)
    with pytest.warns(None) as record:
        matcher.add("TEST3", None, doc3)
        assert not record.list
    matcher = PhraseMatcher(en_vocab, attr="POS", validate=True)
    with pytest.warns(None) as record:
        matcher.add("TEST4", None, doc2)
        assert not record.list
