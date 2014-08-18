from __future__ import unicode_literals

from spacy.en import tokenize, lookup, unhash

from spacy import lex_of


def test_possess():
    tokens = tokenize("Mike's")
    assert unhash(lex_of(tokens[0])) == "Mike"
    assert unhash(lex_of(tokens[1])) == "'s"
    assert len(tokens) == 2


def test_apostrophe():
    tokens = tokenize("schools'")
    assert len(tokens) == 2
    assert unhash(lex_of(tokens[1])) == "'"
    assert unhash(lex_of(tokens[0])) == "schools"


def test_LL():
    tokens = tokenize("we'll")
    assert len(tokens) == 2
    assert unhash(lex_of(tokens[1])) == "will"
    assert unhash(lex_of(tokens[0])) == "we"


def test_aint():
    tokens = tokenize("ain't")
    assert len(tokens) == 2
    assert unhash(lex_of(tokens[0])) == "are"
    assert unhash(lex_of(tokens[1])) == "not"


def test_capitalized():
    tokens = tokenize("can't")
    assert len(tokens) == 2
    tokens = tokenize("Can't")
    assert len(tokens) == 2
    tokens = tokenize("Ain't")
    assert len(tokens) == 2
    assert unhash(lex_of(tokens[0])) == "Are"
