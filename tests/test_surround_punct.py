from __future__ import unicode_literals

from spacy.en import English

import pytest


@pytest.fixture
def paired_puncts():
    return [('(', ')'),  ('[', ']'), ('{', '}'), ('*', '*')]


@pytest.fixture
def EN():
    return English()


def test_token(paired_puncts, EN):
    word_str = 'Hello'
    for open_, close_ in paired_puncts:
        string = open_ + word_str + close_
        tokens = EN(string)
        assert len(tokens) == 3
        assert tokens[0].orth_ == open_
        assert tokens[1].orth_ == word_str
        assert tokens[2].orth_ == close_


def test_two_different(paired_puncts, EN):
    word_str = 'Hello'
    for open_, close_ in paired_puncts:
        string = "`" + open_ + word_str + close_ + "'"
        tokens = EN(string)
        assert len(tokens) == 5
        assert tokens[0].orth_ == "`"
        assert tokens[1].orth_ == open_
        assert tokens[2].orth_ == word_str
        assert tokens[2].orth_ == word_str
        assert tokens[3].orth_ == close_
        assert tokens[4].orth_ == "'"
