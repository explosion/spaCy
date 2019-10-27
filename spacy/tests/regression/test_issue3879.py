# coding: utf8
from __future__ import unicode_literals

from spacy.matcher import Matcher
from spacy.tokens import Doc


def test_issue3879(en_vocab):
    doc = Doc(en_vocab, words=["This", "is", "a", "test", "."])
    assert len(doc) == 5
    pattern = [{"ORTH": "This", "OP": "?"}, {"OP": "?"}, {"ORTH": "test"}]
    matcher = Matcher(en_vocab)
    matcher.add("TEST", [pattern])
    assert len(matcher(doc)) == 2  # fails because of a FP match 'is a test'
