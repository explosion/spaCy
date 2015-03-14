from __future__ import unicode_literals
from spacy.en import English

import pytest

@pytest.fixture
def EN():
    return English()


def test_single_period(EN):
    string = 'A test sentence.'
    words = EN(string)
    assert len(words) == 4
    assert len(list(words.sents)) == 1
    assert sum(len(sent) for sent in words.sents) == len(words)


def test_single_no_period(EN):
    string = 'A test sentence'
    words = EN(string)
    assert len(words) == 3
    assert len(list(words.sents)) == 1
    assert sum(len(sent) for sent in words.sents) == len(words)


def test_single_exclamation(EN):
    string = 'A test sentence!'
    words = EN(string)
    assert len(words) == 4
    assert len(list(words.sents)) == 1
    assert sum(len(sent) for sent in words.sents) == len(words)


def test_single_question(EN):
    string = 'A test sentence?'
    words = EN(string, tag=False, parse=False)
    assert len(words) == 4
    assert len(list(words.sents)) == 1
    assert sum(len(sent) for sent in words.sents) == len(words)
