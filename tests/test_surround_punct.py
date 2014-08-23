from __future__ import unicode_literals

from spacy.en import tokenize
from spacy.en import lookup
from spacy.en import unhash

import pytest


@pytest.fixture
def paired_puncts():
    return [('(', ')'),  ('[', ']'), ('{', '}'), ('*', '*')]


def test_token(paired_puncts):
    word_str = 'Hello'
    for open_, close_ in paired_puncts:
        string = open_ + word_str + close_
        tokens = tokenize(string)
        assert len(tokens) == 3
        assert unhash(tokens[0].lex) == open_
        assert unhash(tokens[1].lex) == word_str
        assert unhash(tokens[2].lex) == close_


def test_two_different(paired_puncts):
    word_str = 'Hello'
    for open_, close_ in paired_puncts:
        string = "`" + open_ + word_str + close_ + "'"
        tokens = tokenize(string)
        assert len(tokens) == 5
        assert unhash(tokens[0].lex) == "`"
        assert unhash(tokens[1].lex) == open_
        assert unhash(tokens[2].lex) == word_str
        assert unhash(tokens[2].lex) == word_str
        assert unhash(tokens[3].lex) == close_
        assert unhash(tokens[4].lex) == "'"
