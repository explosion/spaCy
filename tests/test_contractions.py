from __future__ import unicode_literals
import pytest

from spacy.en import English

@pytest.fixture
def EN():
    return English()


def test_possess(EN):
    tokens = EN("Mike's")
    assert EN.vocab.strings[tokens[0].sic] == b"Mike"
    assert EN.vocab.strings[tokens[1].sic] == b"'s"
    assert len(tokens) == 2


def test_apostrophe(EN):
    tokens = EN("schools'")
    assert len(tokens) == 2
    assert tokens[1].string == b"'"
    assert tokens[0].string == b"schools"


def test_LL(EN):
    tokens = EN("we'll")
    assert len(tokens) == 2
    assert tokens[1].string == b"'ll"
    assert tokens[1].lemma == b"will"
    assert tokens[0].string == b"we"


def test_aint(EN):
    tokens = EN("ain't")
    assert len(tokens) == 2
    assert tokens[0].string == b"ai"
    assert tokens[0].lemma == b"be"
    assert tokens[1].string == b"n't"
    assert tokens[1].lemma == b"not"


def test_capitalized(EN):
    tokens = EN("can't")
    assert len(tokens) == 2
    tokens = EN("Can't")
    assert len(tokens) == 2
    tokens = EN("Ain't")
    assert len(tokens) == 2
    assert tokens[0].string == b"Ai"
    assert tokens[0].lemma == b"be"


def test_punct(EN):
    tokens = EN("We've")
    assert len(tokens) == 2
    tokens = EN("``We've")
    assert len(tokens) == 3
