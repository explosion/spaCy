# coding: utf8
from __future__ import unicode_literals

from spacy.matcher import Matcher
from spacy.tokens import Doc


def test_issue3839(en_vocab):
    """Test that match IDs returned by the matcher are correct, are in the string """
    doc = Doc(en_vocab, words=["terrific", "group", "of", "people"])
    matcher = Matcher(en_vocab)
    match_id = "PATTERN"
    pattern1 = [{"LOWER": "terrific"}, {"OP": "?"}, {"LOWER": "group"}]
    pattern2 = [{"LOWER": "terrific"}, {"OP": "?"}, {"OP": "?"}, {"LOWER": "group"}]
    matcher.add(match_id, None, pattern1)
    matches = matcher(doc)
    assert matches[0][0] == en_vocab.strings[match_id]
    matcher = Matcher(en_vocab)
    matcher.add(match_id, None, pattern2)
    matches = matcher(doc)
    assert matches[0][0] == en_vocab.strings[match_id]
