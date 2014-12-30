from __future__ import unicode_literals
import pytest

from spacy.en import English

@pytest.fixture
def EN():
    return English()


def test_possess(EN):
    tokens = EN("Mike's")
    assert EN.vocab.strings[tokens[0].sic] == "Mike"
    assert EN.vocab.strings[tokens[1].sic] == "'s"
    assert len(tokens) == 2


def test_apostrophe(EN):
    tokens = EN("schools'")
    assert len(tokens) == 2
    assert tokens[1].string == "'"
    assert tokens[0].string == "schools"


def test_LL(EN):
    tokens = EN("we'll")
    assert len(tokens) == 2
    assert tokens[1].string == "'ll"
    assert tokens[1].lemma == "will"
    assert tokens[0].string == "we"


def test_aint(EN):
    tokens = EN("ain't")
    assert len(tokens) == 2
    assert tokens[0].string == "ai"
    assert tokens[0].lemma == "be"
    assert tokens[1].string == "n't"
    assert tokens[1].lemma == "not"


def test_capitalized(EN):
    tokens = EN("can't")
    assert len(tokens) == 2
    tokens = EN("Can't")
    assert len(tokens) == 2
    tokens = EN("Ain't")
    assert len(tokens) == 2
    assert tokens[0].string == "Ai"
    assert tokens[0].lemma == "be"


def test_punct(EN):
    tokens = EN("We've")
    assert len(tokens) == 2
    tokens = EN("``We've")
    assert len(tokens) == 3
