# coding: utf8
from __future__ import unicode_literals

import pytest
from spacy.tokens import Doc, Token
from spacy.matcher import Matcher


@pytest.mark.xfail
def test_issue3555(en_vocab):
    """Test that custom extensions with default None don't break matcher."""
    Token.set_extension("issue3555", default=None)
    matcher = Matcher(en_vocab)
    pattern = [{"LEMMA": "have"}, {"_": {"issue3555": True}}]
    matcher.add("TEST", None, pattern)
    doc = Doc(en_vocab, words=["have", "apple"])
    matcher(doc)
