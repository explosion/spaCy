from __future__ import unicode_literals

from spacy.en import lookup
from spacy.en import tokenize
from spacy.en import unhash

import pytest


@pytest.fixture
def open_puncts():
    return ['(', '[', '{', '*']


def test_open(open_puncts):
    word_str = 'Hello'
    for p in open_puncts:
        string = p + word_str
        tokens = tokenize(string)
        assert len(tokens) == 2
        assert unhash(tokens[0].lex) == p
        assert unhash(tokens[1].lex) == word_str


def test_two_different_open(open_puncts):
    word_str = 'Hello'
    for p in open_puncts:
        string = p + "`" + word_str
        tokens = tokenize(string)
        assert len(tokens) == 3
        assert unhash(tokens[0].lex) == p
        assert unhash(tokens[1].lex) == "`"
        assert unhash(tokens[2].lex) == word_str


def test_three_same_open(open_puncts):
    word_str = 'Hello'
    for p in open_puncts:
        string = p + p + p + word_str
        tokens = tokenize(string)
        assert len(tokens) == 4
        assert unhash(tokens[0].lex) == p
        assert unhash(tokens[3].lex) == word_str


def test_open_appostrophe():
    string = "'The"
    tokens = tokenize(string)
    assert len(tokens) == 2
    assert unhash(tokens[0].lex) == "'"
