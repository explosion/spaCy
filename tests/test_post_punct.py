from __future__ import unicode_literals

from spacy import lex_of
from spacy.spacy import expand_chunk
from spacy.en import lookup
from spacy.en import unhash

import pytest


@pytest.fixture
def close_puncts():
    return [')', ']', '}', '*']


def test_close(close_puncts):
    word_str = 'Hello'
    for p in close_puncts:
        string = word_str + p
        token = lookup(string)
        tokens = expand_chunk(token)
        assert len(tokens) == 2
        assert unhash(lex_of(tokens[1])) == p
        assert unhash(lex_of(tokens[0])) == word_str


def test_two_different_close(close_puncts):
    word_str = 'Hello'
    for p in close_puncts:
        string = word_str + p + "'"
        token = lookup(string)
        assert unhash(lex_of(token)) == word_str
        tokens = expand_chunk(token)
        assert len(tokens) == 3
        assert unhash(lex_of(tokens[0])) == word_str
        assert unhash(lex_of(tokens[1])) == p
        assert unhash(lex_of(tokens[2])) == "'"


def test_three_same_close(close_puncts):
    word_str = 'Hello'
    for p in close_puncts:
        string = word_str + p + p + p
        tokens = expand_chunk(lookup(string))
        assert len(tokens) == 4
        assert unhash(lex_of(tokens[0])) == word_str
        assert unhash(lex_of(tokens[1])) == p
