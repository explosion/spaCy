from __future__ import unicode_literals
import pytest

from spacy.orth import is_alpha
from spacy.orth import is_digit
from spacy.orth import is_punct
from spacy.orth import is_space
from spacy.orth import is_ascii
from spacy.orth import is_upper
from spacy.orth import is_lower
from spacy.orth import is_title


@pytest.fixture
def words():
    return ["1997", "19.97", "hello9", "Hello", "HELLO", "Hello9", "\n", "!",
            "!d", "\nd"]


def test_is_alpha(words):
    assert not is_alpha(words[0])
    assert not is_alpha(words[1])
    assert not is_alpha(words[2])
    assert is_alpha(words[3])
    assert is_alpha(words[4])
    assert not is_alpha(words[5])
    assert not is_alpha(words[6])
    assert not is_alpha(words[7])
    assert not is_alpha(words[8])
    assert not is_alpha(words[9])


def test_is_digit(words):
    assert is_digit(words[0])
    assert not is_digit(words[1])
    assert not is_digit(words[2])
    assert not is_digit(words[3])
    assert not is_digit(words[4])
    assert not is_digit(words[5])
    assert not is_digit(words[6])
    assert not is_digit(words[7])
    assert not is_digit(words[8])
    assert not is_digit(words[9])


def test_is_quote(words):
    pass


def test_is_bracket(words):
    pass


def test_is_left_bracket(words):
    pass

def test_is_right_bracket(words):
    pass
