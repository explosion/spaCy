import pytest

from orth import is_alpha
from orth import is_digit
from orth import is_punct
from orth import is_space
from orth import is_ascii
from orth import is_upper
from orth import is_lower
from orth import is_title


@pytest.fixture
def words():
    return ["1997", "19.97", "hello9", "Hello", "HELLO", "Hello9", "\n", "!",
            "!d", "\nd"]

def test_is_alpha(words):
    assert is_alpha(words[0]) == False
    assert is_alpha(words[1]) == False
    assert is_alpha(words[2]) == False
    assert is_alpha(words[3]) == True
    assert is_alpha(words[4]) == True
    assert is_alpha(words[5]) == False
    assert is_alpha(words[6]) == False
    assert is_alpha(words[7]) == False
    assert is_alpha(words[8]) == False
    assert is_alpha(words[9]) == False


def test_is_digit(words):
    assert is_digit(words[0]) == False
    assert is_digit(words[1]) == False
    assert is_digit(words[2]) == False
    assert is_digit(words[3]) == True
    assert is_digit(words[4]) == True
    assert is_digit(words[5]) == False
    assert is_digit(words[6]) == False
    assert is_digit(words[7]) == False
    assert is_digit(words[8]) == False
    assert is_digit(words[9]) == False
