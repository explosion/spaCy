from __future__ import unicode_literals
import pytest


def test_possess(en_tokenizer):
    tokens = en_tokenizer("Mike's")
    assert en_tokenizer.vocab.strings[tokens[0].orth] == "Mike"
    assert en_tokenizer.vocab.strings[tokens[1].orth] == "'s"
    assert len(tokens) == 2


def test_apostrophe(en_tokenizer):
    tokens = en_tokenizer("schools'")
    assert len(tokens) == 2
    assert tokens[1].orth_ == "'"
    assert tokens[0].orth_ == "schools"


def test_LL(en_tokenizer):
    tokens = en_tokenizer("we'll")
    assert len(tokens) == 2
    assert tokens[1].orth_ == "'ll"
    assert tokens[1].lemma_ == "will"
    assert tokens[0].orth_ == "we"


def test_aint(en_tokenizer):
    tokens = en_tokenizer("ain't")
    assert len(tokens) == 2
    assert tokens[0].orth_ == "ai"
    assert tokens[0].lemma_ == "be"
    assert tokens[1].orth_ == "n't"
    assert tokens[1].lemma_ == "not"

def test_capitalized(en_tokenizer):
    tokens = en_tokenizer("can't")
    assert len(tokens) == 2
    tokens = en_tokenizer("Can't")
    assert len(tokens) == 2
    tokens = en_tokenizer("Ain't")
    assert len(tokens) == 2
    assert tokens[0].orth_ == "Ai"
    assert tokens[0].lemma_ == "be"


def test_punct(en_tokenizer):
    tokens = en_tokenizer("We've")
    assert len(tokens) == 2
    tokens = en_tokenizer("``We've")
    assert len(tokens) == 3


@pytest.mark.xfail
def test_therell(en_tokenizer):
    tokens = en_tokenizer("there'll")
    assert len(tokens) == 2
    assert tokens[0].text == "there"
    assert tokens[1].text == "there"
