# coding: utf8
from __future__ import unicode_literals

import pytest
from spacy.matcher import Matcher
from spacy.tokens import Token, Doc


def test_issue1971(en_vocab):
    # Possibly related to #2675 and #2671?
    matcher = Matcher(en_vocab)
    pattern = [
        {"ORTH": "Doe"},
        {"ORTH": "!", "OP": "?"},
        {"_": {"optional": True}, "OP": "?"},
        {"ORTH": "!", "OP": "?"},
    ]
    Token.set_extension("optional", default=False)
    matcher.add("TEST", None, pattern)
    doc = Doc(en_vocab, words=["Hello", "John", "Doe", "!"])
    # We could also assert length 1 here, but this is more conclusive, because
    # the real problem here is that it returns a duplicate match for a match_id
    # that's not actually in the vocab!
    matches = matcher(doc)
    assert all([match_id in en_vocab.strings for match_id, start, end in matches])


def test_issue_1971_2(en_vocab):
    matcher = Matcher(en_vocab)
    pattern1 = [{"ORTH": "EUR", "LOWER": {"IN": ["eur"]}}, {"LIKE_NUM": True}]
    pattern2 = [{"LIKE_NUM": True}, {"ORTH": "EUR"}] #{"IN": ["EUR"]}}]
    doc = Doc(en_vocab, words=["EUR", "10", "is", "10", "EUR"])
    matcher.add("TEST1", None, pattern1, pattern2)
    matches = matcher(doc)
    assert len(matches) == 2


def test_issue_1971_3(en_vocab):
    """Test that pattern matches correctly for multiple extension attributes."""
    Token.set_extension("a", default=1)
    Token.set_extension("b", default=2)
    doc = Doc(en_vocab, words=["hello", "world"])
    matcher = Matcher(en_vocab)
    matcher.add("A", None, [{"_": {"a": 1}}])
    matcher.add("B", None, [{"_": {"b": 2}}])
    matches = sorted((en_vocab.strings[m_id], s, e) for m_id, s, e in matcher(doc))
    assert len(matches) == 4
    assert matches == sorted([("A", 0, 1), ("A", 1, 2), ("B", 0, 1), ("B", 1, 2)])


def test_issue_1971_4(en_vocab):
    """Test that pattern matches correctly with multiple extension attribute
    values on a single token.
    """
    Token.set_extension("ext_a", default="str_a")
    Token.set_extension("ext_b", default="str_b")
    matcher = Matcher(en_vocab)
    doc = Doc(en_vocab, words=["this", "is", "text"])
    pattern = [{"_": {"ext_a": "str_a", "ext_b": "str_b"}}] * 3
    matcher.add("TEST", None, pattern)
    matches = matcher(doc)
    # Interesting: uncommenting this causes a segmentation fault, so there's
    # definitely something going on here
    # assert len(matches) == 1
