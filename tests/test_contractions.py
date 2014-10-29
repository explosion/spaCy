from __future__ import unicode_literals

from spacy.en import EN


def test_possess():
    tokens = EN.tokenize("Mike's")
    assert EN.lexicon.strings[tokens[0].sic] == "Mike"
    assert EN.lexicon.strings[tokens[1].sic] == "'s"
    assert len(tokens) == 2


def test_apostrophe():
    tokens = EN.tokenize("schools'")
    assert len(tokens) == 2
    assert tokens[1].string == "'"
    assert tokens[0].string == "schools"


def test_LL():
    tokens = EN.tokenize("we'll")
    assert len(tokens) == 2
    assert tokens[1].string == "will"
    assert tokens[0].string == "we"


def test_aint():
    tokens = EN.tokenize("ain't")
    assert len(tokens) == 2
    assert tokens[0].string == "are"
    assert tokens[1].string == "not"


def test_capitalized():
    tokens = EN.tokenize("can't")
    assert len(tokens) == 2
    tokens = EN.tokenize("Can't")
    assert len(tokens) == 2
    tokens = EN.tokenize("Ain't")
    assert len(tokens) == 2
    assert tokens[0].string == "Are"
