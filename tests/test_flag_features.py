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
    assert is_alpha(words[0], 0, {}, {}) == False
    assert is_alpha(words[1], 0, {}, {}) == False
    assert is_alpha(words[2], 0, {}, {}) == False
    assert is_alpha(words[3], 0, {}, {}) == True
    assert is_alpha(words[4], 0, {}, {}) == True
    assert is_alpha(words[5], 0, {}, {}) == False
    assert is_alpha(words[6], 0, {}, {}) == False
    assert is_alpha(words[7], 0, {}, {}) == False
    assert is_alpha(words[8], 0, {}, {}) == False
    assert is_alpha(words[9], 0, {}, {}) == False


def test_is_digit(words):
    assert is_digit(words[0], 0, {}, {}) == True
    assert is_digit(words[1], 0, {}, {}) == False
    assert is_digit(words[2], 0, {}, {}) == False
    assert is_digit(words[3], 0, {}, {}) == False
    assert is_digit(words[4], 0, {}, {}) == False
    assert is_digit(words[5], 0, {}, {}) == False
    assert is_digit(words[6], 0, {}, {}) == False
    assert is_digit(words[7], 0, {}, {}) == False
    assert is_digit(words[8], 0, {}, {}) == False
    assert is_digit(words[9], 0, {}, {}) == False
