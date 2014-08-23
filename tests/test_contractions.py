from __future__ import unicode_literals

from spacy.en import tokenize, lookup, unhash


def test_possess():
    tokens = tokenize("Mike's")
    assert unhash(tokens[0].lex) == "Mike"
    assert unhash(tokens[1].lex) == "'s"
    assert len(tokens) == 2


def test_apostrophe():
    tokens = tokenize("schools'")
    assert len(tokens) == 2
    assert unhash(tokens[1].lex) == "'"
    assert unhash(tokens[0].lex) == "schools"


def test_LL():
    tokens = tokenize("we'll")
    assert len(tokens) == 2
    assert unhash(tokens[1].lex) == "will"
    assert unhash(tokens[0].lex) == "we"


def test_aint():
    tokens = tokenize("ain't")
    assert len(tokens) == 2
    assert unhash(tokens[0].lex) == "are"
    assert unhash(tokens[1].lex) == "not"


def test_capitalized():
    tokens = tokenize("can't")
    assert len(tokens) == 2
    tokens = tokenize("Can't")
    assert len(tokens) == 2
    tokens = tokenize("Ain't")
    assert len(tokens) == 2
    assert unhash(tokens[0].lex) == "Are"
