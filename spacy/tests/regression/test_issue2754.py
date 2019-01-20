# coding: utf8
from __future__ import unicode_literals

import pytest
from spacy.lang.en import English

def test_issue2754():
    """Test that words like 'a' and 'a.m.' don't get exceptional norm values."""
    nlp = English()
    a = nlp('a')
    assert a[0].norm_ == 'a'
    am = nlp('am')
    assert am[0].norm_ == 'am'

