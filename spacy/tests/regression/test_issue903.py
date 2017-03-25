# coding: utf8
from __future__ import unicode_literals

import pytest
from ...tokens import Doc


@pytest.mark.parametrize('text,tag,lemma',
    [("anus", "NN", "anus"),
     ("princess", "NN", "princess")])
def test_issue912(en_vocab, text, tag, lemma):
    '''Test base-forms of adjectives are preserved.'''
    doc = Doc(en_vocab, words=[text])
    doc[0].tag_ = tag
    assert doc[0].lemma_ == lemma

