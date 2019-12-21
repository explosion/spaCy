# coding: utf8
from __future__ import unicode_literals

import pytest


ABBREVIATION_TESTS = [
    (
        "Hyvää uutta vuotta t. siht. Niemelä!",
        ["Hyvää", "uutta", "vuotta", "t.", "siht.", "Niemelä", "!"],
    ),
    ("Paino on n. 2.2 kg", ["Paino", "on", "n.", "2.2", "kg"]),
]

HYPHENATED_TESTS = [
    (
        "1700-luvulle sijoittuva taide-elokuva",
        ["1700-luvulle", "sijoittuva", "taide-elokuva"],
    )
]


@pytest.mark.parametrize("text,expected_tokens", ABBREVIATION_TESTS)
def test_fi_tokenizer_abbreviations(fi_tokenizer, text, expected_tokens):
    tokens = fi_tokenizer(text)
    token_list = [token.text for token in tokens if not token.is_space]
    assert expected_tokens == token_list


@pytest.mark.parametrize("text,expected_tokens", HYPHENATED_TESTS)
def test_fi_tokenizer_hyphenated_words(fi_tokenizer, text, expected_tokens):
    tokens = fi_tokenizer(text)
    token_list = [token.text for token in tokens if not token.is_space]
    assert expected_tokens == token_list
