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
        assert tokens[0].string == open_
        assert tokens[1].string == word_str
        assert tokens[2].string == close_


def test_two_different(paired_puncts, EN):
    word_str = 'Hello'
    for open_, close_ in paired_puncts:
        string = "`" + open_ + word_str + close_ + "'"
        tokens = EN(string)
        assert len(tokens) == 5
        assert tokens[0].string == "`"
        assert tokens[1].string == open_
        assert tokens[2].string == word_str
        assert tokens[2].string == word_str
        assert tokens[3].string == close_
        assert tokens[4].string == "'"
