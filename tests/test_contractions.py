from __future__ import unicode_literals
import pytest

from spacy.en import English

EN = English()

def test_possess():
    tokens = EN("Mike's", parse=False, tag=False)
    assert EN.vocab.strings[tokens[0].orth] == "Mike"
    assert EN.vocab.strings[tokens[1].orth] == "'s"
    assert len(tokens) == 2


def test_apostrophe():
    tokens = EN("schools'", parse=False, tag=False)
    assert len(tokens) == 2
    assert tokens[1].orth_ == "'"
    assert tokens[0].orth_ == "schools"


def test_LL():
    tokens = EN("we'll", parse=False)
    assert len(tokens) == 2
    assert tokens[1].orth_ == "'ll"
    assert tokens[1].lemma_ == "will"
    assert tokens[0].orth_ == "we"


def test_aint():
    tokens = EN("ain't", parse=False)
    assert len(tokens) == 2
    assert tokens[0].orth_ == "ai"
    assert tokens[0].lemma_ == "be"
    assert tokens[1].orth_ == "n't"
    assert tokens[1].lemma_ == "not"


def test_capitalized():
    tokens = EN("can't", parse=False)
    assert len(tokens) == 2
    tokens = EN("Can't", parse=False)
    assert len(tokens) == 2
    tokens = EN("Ain't", parse=False)
    assert len(tokens) == 2
    assert tokens[0].orth_ == "Ai"
    assert tokens[0].lemma_ == "be"


def test_punct():
    tokens = EN("We've", parse=False)
    assert len(tokens) == 2
    tokens = EN("``We've", parse=False)
    assert len(tokens) == 3
