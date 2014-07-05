from __future__ import unicode_literals

from spacy import lex_of, sic_of
from spacy.spacy import expand_chunk
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
        tokens = expand_chunk(lookup(string))
        assert len(tokens) == 3
        assert unhash(lex_of(tokens[0])) == open_
        assert unhash(lex_of(tokens[1])) == word_str
        assert unhash(lex_of(tokens[2])) == close_
        assert unhash(sic_of(tokens[0])) == string


def test_two_different(paired_puncts):
    word_str = 'Hello'
    for open_, close_ in paired_puncts:
        string = "`" + open_ + word_str + close_ + "'"
        tokens = expand_chunk(lookup(string))
        assert len(tokens) == 5
        assert unhash(lex_of(tokens[0])) == "`"
        assert unhash(lex_of(tokens[1])) == open_
        assert unhash(lex_of(tokens[2])) == word_str
        assert unhash(lex_of(tokens[2])) == word_str
        assert unhash(lex_of(tokens[3])) == close_
        assert unhash(lex_of(tokens[4])) == "'"
