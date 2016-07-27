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


@pytest.mark.xfail
@pytest.mark.models
def test_return_char(EN):
    string = ('hi Aaron,\r\n\r\nHow is your schedule today, I was wondering if '
              'you had time for a phone\r\ncall this afternoon?\r\n\r\n\r\n')
    tokens = EN(string)
    for token in tokens:
        if token.is_space:
            assert token.pos == SPACE
    assert tokens[3].text == '\r\n\r\n'
    assert tokens[3].is_space
    assert tokens[3].pos == SPACE
