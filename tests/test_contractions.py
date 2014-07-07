from __future__ import unicode_literals

from spacy.spacy import expand_chunk
from spacy.en import lookup, unhash

from spacy import lex_of


def test_possess():
    tokens = expand_chunk(lookup("Mike's"))
    assert len(tokens) == 2
    assert unhash(lex_of(tokens[0])) == "Mike"
    assert unhash(lex_of(tokens[1])) == "'s"


def test_apostrophe():
    tokens = expand_chunk(lookup("schools'"))
    assert len(tokens) == 2
    assert unhash(lex_of(tokens[1])) == "'"
    assert unhash(lex_of(tokens[0])) == "schools"


def test_LL():
    tokens = expand_chunk(lookup("we'll"))
    assert len(tokens) == 2
    assert unhash(lex_of(tokens[1])) == "will"
    assert unhash(lex_of(tokens[0])) == "we"


def test_aint():
    tokens = expand_chunk(lookup("ain't"))
    assert len(tokens) == 2
    assert unhash(lex_of(tokens[0])) == "are"
    assert unhash(lex_of(tokens[1])) == "not"
