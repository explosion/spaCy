# coding: utf-8
"""Ensure spaces are assigned the POS tag SPACE"""


from __future__ import unicode_literals
from ...parts_of_speech import SPACE

import pytest


@pytest.mark.models
def test_tagger_spaces(EN):
    text = "Some\nspaces are\tnecessary."
    doc = EN(text, tag=True, parse=False)
    assert doc[0].pos != SPACE
    assert doc[0].pos_ != 'SPACE'
    assert doc[1].pos == SPACE
    assert doc[1].pos_ == 'SPACE'
    assert doc[1].tag_ == 'SP'
    assert doc[2].pos != SPACE
    assert doc[3].pos != SPACE
    assert doc[4].pos == SPACE


@pytest.mark.models
def test_tagger_return_char(EN):
    text = ('hi Aaron,\r\n\r\nHow is your schedule today, I was wondering if '
              'you had time for a phone\r\ncall this afternoon?\r\n\r\n\r\n')
    tokens = EN(text)
    for token in tokens:
        if token.is_space:
            assert token.pos == SPACE
    assert tokens[3].text == '\r\n\r\n'
    assert tokens[3].is_space
    assert tokens[3].pos == SPACE
