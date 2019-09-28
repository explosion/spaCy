# coding: utf-8
from __future__ import unicode_literals

import pytest
from spacy.lang.da.lex_attrs import like_num


def test_da_tokenizer_handles_long_text(da_tokenizer):
    text = """Der var så dejligt ude på landet. Det var sommer, kornet stod gult, havren grøn,
høet var rejst i stakke nede i de grønne enge, og der gik storken på sine lange,
røde ben og snakkede ægyptisk, for det sprog havde han lært af sin moder.

Rundt om ager og eng var der store skove, og midt i skovene dybe søer; jo, der var rigtignok dejligt derude på landet!"""
    tokens = da_tokenizer(text)
    assert len(tokens) == 84


@pytest.mark.parametrize(
    "text,match",
    [
        ("10", True),
        ("1", True),
        ("10.000", True),
        ("10.00", True),
        ("999,0", True),
        ("en", True),
        ("treoghalvfemsindstyvende", True),
        ("hundrede", True),
        ("hund", False),
        (",", False),
        ("1/2", True),
    ],
)
def test_lex_attrs_like_number(da_tokenizer, text, match):
    tokens = da_tokenizer(text)
    assert len(tokens) == 1
    assert tokens[0].like_num == match


@pytest.mark.parametrize("word", ["elleve", "første"])
def test_da_lex_attrs_capitals(word):
    assert like_num(word)
    assert like_num(word.upper())
