# coding: utf-8
from __future__ import unicode_literals

import pytest


def test_eu_tokenizer_handles_long_text(eu_tokenizer):
    text = """ta nere guitarra estrenatu ondoren"""
    tokens = eu_tokenizer(text)
    assert len(tokens) == 5


@pytest.mark.parametrize(
    "text,length",
    [
        ("milesker ederra joan zen hitzaldia plazer hutsa", 7),
        ("astelehen guztia sofan pasau biot", 5),
    ],
)
def test_eu_tokenizer_handles_cnts(eu_tokenizer, text, length):
    tokens = eu_tokenizer(text)
    assert len(tokens) == length
