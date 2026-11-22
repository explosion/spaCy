import unicodedata

import pytest

from spacy.lang.yo.stop_words import STOP_WORDS

# Fragments that are not standalone Yoruba words. See #14036.
FRAGMENTS = [
    "b",
    "d",
    "f",
    "g",
    "j",
    "k",
    "l",
    "p",
    "r",
    "s",
    "t",
    "w",
    "y",
    "\u1e63",  # s with dot below
    "e",
    "i",
    "u",
    "\u00e0",  # a with grave
    "\u00e8",  # e with grave
    "\u00ec",  # i with grave
    "\u00f9",  # u with grave
    "\u0300",  # bare combining grave
    "\u0301",  # bare combining acute
    "\u0323",  # bare combining dot below
]

# Single-character entries that are real Yoruba words.
SINGLE_CHAR_WORDS = [
    "\u00f3",  # he/she/it
    "\u0144",  # progressive marker
    "\u00f2",  # negation
    "\u00ed",  # object pronoun
]


def test_yo_stop_words_are_nfc():
    for word in STOP_WORDS:
        assert unicodedata.is_normalized("NFC", word), ascii(word)


def test_yo_stop_words_do_not_start_with_combining_mark():
    for word in STOP_WORDS:
        assert not unicodedata.combining(word[0]), ascii(word)


@pytest.mark.parametrize("fragment", FRAGMENTS)
def test_yo_stop_words_exclude_fragments(fragment):
    assert fragment not in STOP_WORDS


@pytest.mark.parametrize("word", SINGLE_CHAR_WORDS)
def test_yo_stop_words_keep_single_char_words(word):
    assert word in STOP_WORDS