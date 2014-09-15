# coding: utf-8
from __future__ import unicode_literals

from spacy.en import EN


def test_single_word():
    lex_ids = EN.tokenize(u'hello')
    assert lex_ids[0].string == EN.lexicon.lookup(u'hello').string


def test_two_words():
    words = EN.tokenize('hello possums')
    assert len(words) == 2
    assert words[0].string == EN.lexicon.lookup('hello').string
    assert words[0].string != words[1].string


def test_punct():
    tokens = EN.tokenize('hello, possums.')
    assert len(tokens) == 4
    assert tokens[0].string == EN.lexicon.lookup('hello').string
    assert tokens[1].string == EN.lexicon.lookup(',').string
    assert tokens[2].string == EN.lexicon.lookup('possums').string
    assert tokens[1].string != EN.lexicon.lookup('hello').string


def test_digits():
    lex_ids = EN.tokenize('The year: 1984.')
    assert lex_ids.string(3) == "1984"
    assert len(lex_ids) == 5
    assert lex_ids[0].string == EN.lexicon.lookup('The').string
    assert lex_ids[3].string == EN.lexicon.lookup('1984').string


def test_contraction():
    lex_ids = EN.tokenize("don't giggle")
    assert len(lex_ids) == 3
    assert lex_ids[1].string == EN.lexicon.lookup("not").string
    lex_ids = EN.tokenize("i said don't!")
    assert len(lex_ids) == 5
    assert lex_ids[4].string == EN.lexicon.lookup('!').string


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
    assert len(tokens) == 6

def test_cnts4():
    text = u"""Yes! "I'd rather have a walk", Ms. Comble sighed. """
    tokens = EN.tokenize(text)
    assert len(tokens) == 15

def test_cnts5():
    text = """'Me too!', Mr. P. Delaware cried. """
    tokens = EN.tokenize(text)
    assert len(tokens) == 11

def test_cnts6():
    text = u'They ran about 10km.'
    tokens = EN.tokenize(text)
    assert len(tokens) == 6

def test_cnts7():
    text = 'But then the 6,000-year ice age came...'
    tokens = EN.tokenize(text)
    assert len(tokens) == 8
