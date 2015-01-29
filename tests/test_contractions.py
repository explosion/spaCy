from __future__ import unicode_literals
import pytest

from spacy.en import English

@pytest.fixture
def EN():
    return English()


def test_possess(EN):
    tokens = EN("Mike's", parse=False)
    assert EN.vocab.strings[tokens[0].orth] == "Mike"
    assert EN.vocab.strings[tokens[1].orth] == "'s"
    assert len(tokens) == 2


def test_apostrophe(EN):
    tokens = EN("schools'")
    assert len(tokens) == 2
    assert tokens[1].orth_ == "'"
    assert tokens[0].orth_ == "schools"


def test_LL(EN):
    tokens = EN("we'll", parse=False)
    assert len(tokens) == 2
    assert tokens[1].orth_ == "'ll"
    assert tokens[1].lemma_ == "will"
    assert tokens[0].orth_ == "we"


def test_aint(EN):
    tokens = EN("ain't", parse=False)
    assert len(tokens) == 2
    assert tokens[0].orth_ == "ai"
    assert tokens[0].lemma_ == "be"
    assert tokens[1].orth_ == "n't"
    assert tokens[1].lemma_ == "not"


def test_capitalized(EN):
    tokens = EN("can't", parse=False)
    assert len(tokens) == 2
    tokens = EN("Can't", parse=False)
    assert len(tokens) == 2
    tokens = EN("Ain't", parse=False)
    assert len(tokens) == 2
    assert tokens[0].orth_ == "Ai"
    assert tokens[0].lemma_ == "be"


def test_punct(EN):
    tokens = EN("We've", parse=False)
    assert len(tokens) == 2
    tokens = EN("``We've", parse=False)
    assert len(tokens) == 3
