from __future__ import unicode_literals
import pytest


@pytest.fixture
def paired_puncts():
    return [('(', ')'),  ('[', ']'), ('{', '}'), ('*', '*')]


def test_token(paired_puncts, en_tokenizer):
    word_str = 'Hello'
    for open_, close_ in paired_puncts:
        string = open_ + word_str + close_
        tokens = en_tokenizer(string)
        assert len(tokens) == 3
        assert tokens[0].orth_ == open_
        assert tokens[1].orth_ == word_str
        assert tokens[2].orth_ == close_


def test_two_different(paired_puncts, en_tokenizer):
    word_str = 'Hello'
    for open_, close_ in paired_puncts:
        string = "`" + open_ + word_str + close_ + "'"
        tokens = en_tokenizer(string)
        assert len(tokens) == 5
        assert tokens[0].orth_ == "`"
        assert tokens[1].orth_ == open_
        assert tokens[2].orth_ == word_str
        assert tokens[2].orth_ == word_str
        assert tokens[3].orth_ == close_
        assert tokens[4].orth_ == "'"
