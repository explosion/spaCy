from __future__ import unicode_literals

from spacy.en import tokenize
from spacy.en import lookup

from spacy.lexeme import lex_of


def test_single_word():
    lex_ids = tokenize(u'hello')
    assert lex_ids[0] == lookup(u'hello')


def test_two_words():
    lex_ids = tokenize(u'hello possums')
    assert len(lex_ids) == 2
    assert lex_ids[0] == lookup(u'hello')
    assert lex_ids[0] != lex_ids[1]


def test_punct():
    tokens = tokenize('hello, possums.')
    assert len(tokens) == 4
    assert lex_of(tokens[0]) == lex_of(lookup('hello'))
    assert lex_of(tokens[1]) == lex_of(lookup(','))
    assert lex_of(tokens[2]) == lex_of(lookup('possums'))
    assert lex_of(tokens[1]) != lex_of(lookup('hello'))


def test_digits():
    lex_ids = tokenize('The year: 1984.')
    assert len(lex_ids) == 5
    assert lex_of(lex_ids[0]) == lex_of(lookup('The'))
    assert lex_of(lex_ids[3]) == lex_of(lookup('1984'))
    assert lex_of(lex_ids[4]) == lex_of(lookup('.'))


def test_contraction():
    lex_ids = tokenize("don't giggle")
    assert len(lex_ids) == 3
    assert lex_of(lex_ids[1]) == lex_of(lookup("not"))
    lex_ids = tokenize("i said don't!")
    assert len(lex_ids) == 4
    assert lex_of(lex_ids[3]) == lex_of(lookup('!'))
