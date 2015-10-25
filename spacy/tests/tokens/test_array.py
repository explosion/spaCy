# coding: utf-8
from __future__ import unicode_literals

import pytest

from spacy import attrs


def test_attr_of_token(EN):
    text = u'An example sentence.'
    tokens = EN(text, tag=True, parse=False)
    example = EN.vocab[u'example']
    assert example.orth != example.shape
    feats_array = tokens.to_array((attrs.ORTH, attrs.SHAPE))
    assert feats_array[0][0] != feats_array[0][1]


@pytest.mark.models
def test_tag(EN):
    text = u'A nice sentence.'
    tokens = EN(text)
    assert tokens[0].tag != tokens[1].tag != tokens[2].tag != tokens[3].tag
    feats_array = tokens.to_array((attrs.ORTH, attrs.TAG))
    assert feats_array[0][1] == tokens[0].tag
    assert feats_array[1][1] == tokens[1].tag
    assert feats_array[2][1] == tokens[2].tag
    assert feats_array[3][1] == tokens[3].tag


@pytest.mark.models
def test_dep(EN):
    text = u'A nice sentence.'
    tokens = EN(text)
    feats_array = tokens.to_array((attrs.ORTH, attrs.DEP))
    assert feats_array[0][1] == tokens[0].dep
    assert feats_array[1][1] == tokens[1].dep
    assert feats_array[2][1] == tokens[2].dep
    assert feats_array[3][1] == tokens[3].dep
