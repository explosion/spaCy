from __future__ import unicode_literals

import pytest


@pytest.fixture
def open_puncts():
    return ['(', '[', '{', '*']


def test_open(open_puncts, en_tokenizer):
    word_str = 'Hello'
    for p in open_puncts:
        string = p + word_str
        tokens = en_tokenizer(string)
        assert len(tokens) == 2
        assert tokens[0].orth_ == p
        assert tokens[1].orth_ == word_str


def test_two_different_open(open_puncts, en_tokenizer):
    word_str = 'Hello'
    for p in open_puncts:
        string = p + "`" + word_str
        tokens = en_tokenizer(string)
        assert len(tokens) == 3
        assert tokens[0].orth_ == p
        assert tokens[1].orth_ == "`"
        assert tokens[2].orth_ == word_str


def test_three_same_open(open_puncts, en_tokenizer):
    word_str = 'Hello'
    for p in open_puncts:
        string = p + p + p + word_str
        tokens = en_tokenizer(string)
        assert len(tokens) == 4
        assert tokens[0].orth_ == p
        assert tokens[3].orth_ == word_str


def test_open_appostrophe(en_tokenizer):
    string = "'The"
    tokens = en_tokenizer(string)
    assert len(tokens) == 2
    assert tokens[0].orth_ == "'"
