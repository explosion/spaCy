# coding: utf8
from __future__ import unicode_literals

import pytest
from spacy.matcher import Matcher
from spacy.tokens import Token, Doc


@pytest.mark.xfail
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
    assert all(match_id in en_vocab.strings for match_id, start, end in matcher(doc))


@pytest.mark.xfail
def test_issue_1971_2(en_vocab):
    matcher = Matcher(en_vocab)
    pattern1 = [{"LOWER": {"IN": ["eur"]}}, {"LIKE_NUM": True}]
    pattern2 = list(reversed(pattern1))
    doc = Doc(en_vocab, words=["EUR", "10", "is", "10", "EUR"])
    matcher.add("TEST", None, pattern1, pattern2)
    matches = matcher(doc)
    assert len(matches) == 2
