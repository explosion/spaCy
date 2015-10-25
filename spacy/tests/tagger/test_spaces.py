"""Ensure spaces are assigned the POS tag SPACE"""


from __future__ import unicode_literals
from spacy.parts_of_speech import SPACE

import pytest



@pytest.fixture
def tagged(EN):
    string = u'Some\nspaces are\tnecessary.'
    tokens = EN(string, tag=True, parse=False)
    return tokens

@pytest.mark.models
def test_spaces(tagged):
    assert tagged[0].pos != SPACE
    assert tagged[0].pos_ != 'SPACE'
    assert tagged[1].pos == SPACE
    assert tagged[1].pos_ == 'SPACE'
    assert tagged[1].tag_ == 'SP'
    assert tagged[2].pos != SPACE
    assert tagged[3].pos != SPACE
    assert tagged[4].pos == SPACE

