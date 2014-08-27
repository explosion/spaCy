from __future__ import unicode_literals

from spacy.en import EN

import pytest


@pytest.fixture
def open_puncts():
    return ['(', '[', '{', '*']


def test_open(open_puncts):
    word_str = 'Hello'
    for p in open_puncts:
        string = p + word_str
        tokens = EN.tokenize(string)
        assert len(tokens) == 2
        assert tokens[0].string == p
        assert tokens[1].string == word_str


def test_two_different_open(open_puncts):
    word_str = 'Hello'
    for p in open_puncts:
        string = p + "`" + word_str
        tokens = EN.tokenize(string)
        assert len(tokens) == 3
        assert tokens[0].string == p
        assert tokens[1].string == "`"
        assert tokens[2].string == word_str


def test_three_same_open(open_puncts):
    word_str = 'Hello'
    for p in open_puncts:
        string = p + p + p + word_str
        tokens = EN.tokenize(string)
        assert len(tokens) == 4
        assert tokens[0].string == p
        assert tokens[3].string == word_str


def test_open_appostrophe():
    string = "'The"
    tokens = EN.tokenize(string)
    assert len(tokens) == 2
    assert tokens[0].string == "'"
