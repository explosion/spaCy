# coding: utf8
from __future__ import unicode_literals

from spacy.matcher import Matcher
from spacy.tokens import Doc


def test_issue3951(en_vocab):
    """Test that combinations of optional rules are matched correctly."""
    matcher = Matcher(en_vocab)
    pattern = [
        {"LOWER": "hello"},
        {"LOWER": "this", "OP": "?"},
        {"OP": "?"},
        {"LOWER": "world"},
    ]
    matcher.add("TEST", [pattern])
    doc = Doc(en_vocab, words=["Hello", "my", "new", "world"])
    matches = matcher(doc)
    assert len(matches) == 0
