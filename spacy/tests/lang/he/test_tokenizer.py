# encoding: utf8
from __future__ import unicode_literals
from spacy.lang.he.lex_attrs import like_num

import pytest


@pytest.mark.parametrize(
    "text,expected_tokens",
    [("פייתון היא שפת תכנות דינמית", ["פייתון", "היא", "שפת", "תכנות", "דינמית"])],
)
def test_he_tokenizer_handles_abbreviation(he_tokenizer, text, expected_tokens):
    tokens = he_tokenizer(text)
    token_list = [token.text for token in tokens if not token.is_space]
    assert expected_tokens == token_list


@pytest.mark.parametrize(
    "text,expected_tokens",
    [
        (
            "עקבת אחריו בכל רחבי המדינה.",
            ["עקבת", "אחריו", "בכל", "רחבי", "המדינה", "."],
        ),
        (
            "עקבת אחריו בכל רחבי המדינה?",
            ["עקבת", "אחריו", "בכל", "רחבי", "המדינה", "?"],
        ),
        (
            "עקבת אחריו בכל רחבי המדינה!",
            ["עקבת", "אחריו", "בכל", "רחבי", "המדינה", "!"],
        ),
        (
            "עקבת אחריו בכל רחבי המדינה..",
            ["עקבת", "אחריו", "בכל", "רחבי", "המדינה", ".."],
        ),
        (
            "עקבת אחריו בכל רחבי המדינה...",
            ["עקבת", "אחריו", "בכל", "רחבי", "המדינה", "..."],
        ),
    ],
)
def test_he_tokenizer_handles_punct(he_tokenizer, text, expected_tokens):
    tokens = he_tokenizer(text)
    assert expected_tokens == [token.text for token in tokens]



@pytest.mark.parametrize(
    "text,match",
    [
        ("10", True),
        ("1", True),
        ("10,000", True),
        ("10,00", True),
        ("999.0", True),
        ("אחד", True),
        ("שתיים", True),
        ("מליון", True),
        ("כלב", False),
        (",", False),
        ("1/2", True),
    ],
)
def test_lex_attrs_like_number(he_tokenizer, text, match):
    tokens = he_tokenizer(text)
    assert len(tokens) == 1
    assert tokens[0].like_num == match


@pytest.mark.parametrize(
    "word",
    [
        "שלישי",
        "מליון",
        "עשירי",
        "מאה",
        "עשר",
        "אחד עשר",
    ]
)
def test_he_lex_attrs_like_number_for_ordinal(word):
    assert like_num(word)
