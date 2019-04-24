# coding: utf8
from __future__ import unicode_literals

from spacy.lang.de import German


def test_issue3002():
    """Test that the tokenizer doesn't hang on a long list of dots"""
    nlp = German()
    doc = nlp('880.794.982.218.444.893.023.439.794.626.120.190.780.624.990.275.671 ist eine lange Zahl')
    assert len(doc) == 5
