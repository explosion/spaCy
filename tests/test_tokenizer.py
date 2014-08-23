from __future__ import unicode_literals

from spacy.en import tokenize
from spacy.en import lookup


def test_single_word():
    lex_ids = tokenize(u'hello')
    assert lex_ids[0] == lookup(u'hello')


def test_two_words():
    words = tokenize('hello possums')
    assert len(words) == 2
    assert words[0] == lookup('hello')
    assert words[0] != words[1]


def test_punct():
    tokens = tokenize('hello, possums.')
    assert len(tokens) == 4
    assert tokens[0].lex == lookup('hello').lex
    assert tokens[1].lex == lookup(',').lex
    assert tokens[2].lex == lookup('possums').lex
    assert tokens[1].lex != lookup('hello').lex


def test_digits():
    lex_ids = tokenize('The year: 1984.')
    assert len(lex_ids) == 5
    assert lex_ids[0].lex == lookup('The').lex
    assert lex_ids[3].lex == lookup('1984').lex
    assert lex_ids[4].lex == lookup('.').lex


def test_contraction():
    lex_ids = tokenize("don't giggle")
    assert len(lex_ids) == 3
    assert lex_ids[1].lex == lookup("not").lex
    lex_ids = tokenize("i said don't!")
    assert len(lex_ids) == 4
    assert lex_ids[3].lex == lookup('!').lex
