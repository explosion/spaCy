# coding: utf-8
from __future__ import unicode_literals

from spacy.en import EN


def test_single_word():
    tokens = EN.tokenize(u'hello')
    assert tokens[0].string == 'hello'


def test_two_words():
    tokens = EN.tokenize('hello possums')
    assert len(tokens) == 2
    assert tokens[0].string != tokens[1].string


def test_punct():
    tokens = EN.tokenize('hello, possums.')
    assert len(tokens) == 4
    assert tokens[0].string == 'hello'
    assert tokens[1].string == ','
    assert tokens[2].string == 'possums'
    assert tokens[1].string != 'hello'


def test_digits():
    tokens = EN.tokenize('The year: 1984.')
    assert len(tokens) == 5
    assert tokens[0].sic == EN.lexicon['The']['sic']
    assert tokens[3].sic == EN.lexicon['1984']['sic']


def test_contraction():
    tokens = EN.tokenize("don't giggle")
    assert len(tokens) == 3
    assert tokens[1].sic == EN.lexicon["n't"]['sic']
    tokens = EN.tokenize("i said don't!")
    assert len(tokens) == 5
    assert tokens[4].sic == EN.lexicon['!']['sic']


def test_contraction_punct():
    tokens = EN.tokenize("(can't")
    assert len(tokens) == 3
    tokens = EN.tokenize("`ain't")
    assert len(tokens) == 3
    tokens = EN.tokenize('''"isn't''')
    assert len(tokens) == 3
    tokens = EN.tokenize("can't!")
    assert len(tokens) == 3

def test_sample():
    text = """Tributes pour in for late British Labour Party leader

Tributes poured in from around the world Thursday 
to the late Labour Party leader John Smith, who died earlier from a massive 
heart attack aged 55.

In Washington, the US State Department issued a statement regretting "the 
untimely death" of the rapier-tongued Scottish barrister and parliamentarian.

"Mr. Smith, throughout his distinguished"""
    
    tokens = EN.tokenize(text)
    assert len(tokens) > 5


def test_cnts1():
    text = u"""The U.S. Army likes Shock and Awe."""
    tokens = EN.tokenize(text)
    assert len(tokens) == 8


def test_cnts2():
    text = u"""U.N. regulations are not a part of their concern."""
    tokens = EN.tokenize(text)
    assert len(tokens) == 10


def test_cnts3():
    text = u"“Isn't it?”"
    tokens = EN.tokenize(text)
    words = [t.string for t in tokens]
    assert len(words) == 6


def test_cnts4():
    text = u"""Yes! "I'd rather have a walk", Ms. Comble sighed. """
    tokens = EN.tokenize(text)
    words = [t.string for t in tokens]
    assert len(words) == 15


def test_cnts5():
    text = """'Me too!', Mr. P. Delaware cried. """
    tokens = EN.tokenize(text)
    assert len(tokens) == 11


def test_cnts6():
    text = u'They ran about 10km.'
    tokens = EN.tokenize(text)
    words = [t.string for t in tokens]
    assert len(words) == 6


#def test_cnts7():
#    text = 'But then the 6,000-year ice age came...'
#    tokens = EN.tokenize(text)
#    assert len(tokens) == 10
