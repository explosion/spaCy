# coding: utf-8
from __future__ import unicode_literals

import pytest

from spacy.en import English
from spacy.en import attrs


EN = English()

def test_attr_of_token():
    text = u'An example sentence.'
    tokens = EN(text)
    example = EN.vocab[u'example']
    assert example.orth != example.shape
    feats_array = tokens.to_array((attrs.ORTH, attrs.SHAPE))
    assert feats_array[0][0] != feats_array[0][1]


def test_tag():
    text = u'A nice sentence.'
    tokens = EN(text)
    assert tokens[0].tag != tokens[1].tag != tokens[2].tag != tokens[3].tag
    feats_array = tokens.to_array((attrs.ORTH, attrs.TAG))
    assert feats_array[0][1] == tokens[0].tag
    assert feats_array[1][1] == tokens[1].tag
    assert feats_array[2][1] == tokens[2].tag
    assert feats_array[3][1] == tokens[3].tag


def test_dep():
    text = u'A nice sentence.'
    tokens = EN(text)
    feats_array = tokens.to_array((attrs.ORTH, attrs.DEP))
    assert feats_array[0][1] == tokens[0].dep
    assert feats_array[1][1] == tokens[1].dep
    assert feats_array[2][1] == tokens[2].dep
    assert feats_array[3][1] == tokens[3].dep


