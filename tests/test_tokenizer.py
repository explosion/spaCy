# coding: utf-8
from __future__ import unicode_literals

import pytest

from spacy.en import English


@pytest.fixture
def EN():
    return English()

def test_single_word(EN):
    tokens = EN(u'hello')
    assert tokens[0].string == 'hello'


def test_two_words(EN):
    tokens = EN('hello possums')
    assert len(tokens) == 2
    assert tokens[0].string != tokens[1].string


def test_punct(EN):
    tokens = EN('hello, possums.')
    assert len(tokens) == 4
    assert tokens[0].string == 'hello'
    assert tokens[1].string == ','
    assert tokens[2].string == 'possums'
    assert tokens[1].string != 'hello'


def test_digits(EN):
    tokens = EN('The year: 1984.')
    assert len(tokens) == 5
    assert tokens[0].sic == EN.vocab['The'].sic
    assert tokens[3].sic == EN.vocab['1984'].sic


def test_contraction(EN):
    tokens = EN("don't giggle")
    assert len(tokens) == 3
    assert tokens[1].sic == EN.vocab["n't"].sic
    tokens = EN("i said don't!")
    assert len(tokens) == 5
    assert tokens[4].sic == EN.vocab['!'].sic


def test_contraction_punct(EN):
    tokens = EN("(can't")
    assert len(tokens) == 3
    tokens = EN("`ain't")
    assert len(tokens) == 3
    tokens = EN('''"isn't''')
    assert len(tokens) == 3
    tokens = EN("can't!")
    assert len(tokens) == 3

def test_sample(EN):
    text = """Tributes pour in for late British Labour Party leader

Tributes poured in from around the world Thursday 
to the late Labour Party leader John Smith, who died earlier from a massive 
heart attack aged 55.

In Washington, the US State Department issued a statement regretting "the 
untimely death" of the rapier-tongued Scottish barrister and parliamentarian.

"Mr. Smith, throughout his distinguished"""
    
    tokens = EN(text)
    assert len(tokens) > 5


def test_cnts1(EN):
    text = u"""The U.S. Army likes Shock and Awe."""
    tokens = EN(text)
    assert len(tokens) == 8


def test_cnts2(EN):
    text = u"""U.N. regulations are not a part of their concern."""
    tokens = EN(text)
    assert len(tokens) == 10


def test_cnts3(EN):
    text = u"“Isn't it?”"
    tokens = EN(text)
    words = [t.string for t in tokens]
    assert len(words) == 6


def test_cnts4(EN):
    text = u"""Yes! "I'd rather have a walk", Ms. Comble sighed. """
    tokens = EN(text)
    words = [t.string for t in tokens]
    assert len(words) == 15


def test_cnts5(EN):
    text = """'Me too!', Mr. P. Delaware cried. """
    tokens = EN(text)
    assert len(tokens) == 11


def test_cnts6(EN):
    text = u'They ran about 10km.'
    tokens = EN(text)
    words = [t.string for t in tokens]
    assert len(words) == 6

#def test_cnts7():
#    text = 'But then the 6,000-year ice age came...'
#    tokens = EN.tokenize(text)
#    assert len(tokens) == 10
