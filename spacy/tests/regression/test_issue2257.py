# coding: utf8
from __future__ import unicode_literals

import pytest
from ...tokens import Doc


@pytest.mark.parametrize('text,tag,lemma', [("coding", "VBG", "code"), ("riding", "VBG", "ride")])
def test_issue2257(en_vocab, text, tag, lemma):
    '''Test base-forms of adjectives are preserved.'''
    doc = Doc(en_vocab, words=[text])
    doc[0].tag_ = tag
    assert doc[0].lemma_ == lemma

