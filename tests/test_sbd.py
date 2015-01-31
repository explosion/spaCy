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
    assert list(words.sents) == [(0, 4)]


def test_single_no_period(EN):
    string = 'A test sentence'
    words = EN(string)
    assert len(words) == 3
    assert list(words.sents) == [(0, 3)]


def test_single_exclamation(EN):
    string = 'A test sentence!'
    words = EN(string)
    assert len(words) == 4
    assert list(words.sents) == [(0, 4)]


def test_single_question(EN):
    string = 'A test sentence?'
    words = EN(string, tag=False, parse=False)
    assert len(words) == 4
    assert list(words.sents) == [(0, 4)]


def test_(EN):
    string = 'A test sentence?'
    words = EN(string, tag=False, parse=False)
    assert len(words) == 4
    assert list(words.sents) == [(0, 4)]
