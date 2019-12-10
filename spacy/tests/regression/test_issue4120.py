# coding: utf8
from __future__ import unicode_literals

from spacy.matcher import Matcher
from spacy.tokens import Doc


def test_issue4120(en_vocab):
    """Test that matches without a final {OP: ?} token are returned."""
    matcher = Matcher(en_vocab)
    matcher.add("TEST", [[{"ORTH": "a"}, {"OP": "?"}]])
    doc1 = Doc(en_vocab, words=["a"])
    assert len(matcher(doc1)) == 1  # works

    doc2 = Doc(en_vocab, words=["a", "b", "c"])
    assert len(matcher(doc2)) == 2  # fixed

    matcher = Matcher(en_vocab)
    matcher.add("TEST", [[{"ORTH": "a"}, {"OP": "?"}, {"ORTH": "b"}]])
    doc3 = Doc(en_vocab, words=["a", "b", "b", "c"])
    assert len(matcher(doc3)) == 2  # works

    matcher = Matcher(en_vocab)
    matcher.add("TEST", [[{"ORTH": "a"}, {"OP": "?"}, {"ORTH": "b", "OP": "?"}]])
    doc4 = Doc(en_vocab, words=["a", "b", "b", "c"])
    assert len(matcher(doc4)) == 3  # fixed
