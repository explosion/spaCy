# coding: utf8
from __future__ import unicode_literals

import pytest
from spacy.matcher import Matcher
from spacy.errors import MatchPatternError


def test_issue3549(en_vocab):
    """Test that match pattern validation doesn't raise on empty errors."""
    matcher = Matcher(en_vocab, validate=True)
    pattern = [{"LOWER": "hello"}, {"LOWER": "world"}]
    matcher.add("GOOD", [pattern])
    with pytest.raises(MatchPatternError):
        matcher.add("BAD", [[{"X": "Y"}]])
