# coding: utf8
from __future__ import unicode_literals

from spacy.lang.es import Spanish


def test_issue3803():
    """Test that spanish num-like tokens have True for like_num attribute."""
    nlp = Spanish()
    text = "2 dos 1000 mil 12 doce"
    doc = nlp(text)

    assert [t.like_num for t in doc] == [True, True, True, True, True, True]
