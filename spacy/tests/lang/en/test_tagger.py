# coding: utf-8
from __future__ import unicode_literals

from ....parts_of_speech import SPACE
from ....compat import unicode_
from ...util import get_doc

import pytest


def test_en_tagger_load_morph_exc(en_tokenizer):
    text = "I like his style."
    tags = ['PRP', 'VBP', 'PRP$', 'NN', '.']
    morph_exc = {'VBP': {'like': {'lemma': 'luck'}}}
    en_tokenizer.vocab.morphology.load_morph_exceptions(morph_exc)
    tokens = en_tokenizer(text)
    doc = get_doc(tokens.vocab, [t.text for t in tokens], tags=tags)
    assert doc[1].tag_ == 'VBP'
    assert doc[1].lemma_ == 'luck'


@pytest.mark.models('en')
def test_tag_names(EN):
    text = "I ate pizzas with anchovies."
    doc = EN(text, disable=['parser'])
    assert type(doc[2].pos) == int
    assert isinstance(doc[2].pos_, unicode_)
    assert isinstance(doc[2].dep_, unicode_)
    assert doc[2].tag_ == u'NNS'


@pytest.mark.xfail
@pytest.mark.models('en')
def test_en_tagger_spaces(EN):
    """Ensure spaces are assigned the POS tag SPACE"""
    text = "Some\nspaces are\tnecessary."
    doc = EN(text, disable=['parser'])
    assert doc[0].pos != SPACE
    assert doc[0].pos_ != 'SPACE'
    assert doc[1].pos == SPACE
    assert doc[1].pos_ == 'SPACE'
    assert doc[1].tag_ == 'SP'
    assert doc[2].pos != SPACE
    assert doc[3].pos != SPACE
    assert doc[4].pos == SPACE


@pytest.mark.xfail
@pytest.mark.models('en')
def test_en_tagger_return_char(EN):
    """Ensure spaces are assigned the POS tag SPACE"""
    text = ('hi Aaron,\r\n\r\nHow is your schedule today, I was wondering if '
              'you had time for a phone\r\ncall this afternoon?\r\n\r\n\r\n')
    tokens = EN(text)
    for token in tokens:
        if token.is_space:
            assert token.pos == SPACE
    assert tokens[3].text == '\r\n\r\n'
    assert tokens[3].is_space
    assert tokens[3].pos == SPACE
