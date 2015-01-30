# coding: utf-8
from __future__ import unicode_literals

import pytest

from spacy.en import English
from spacy.en import attrs


@pytest.fixture
def EN():
    return English()

def test_attr_of_token(EN):
    text = u'An example sentence.'
    tokens = EN(text)
    example = EN.vocab[u'example']
    assert example.orth != example.shape
    feats_array = tokens.to_array((attrs.ORTH, attrs.SHAPE))
    assert feats_array[0][0] != feats_array[0][1]


