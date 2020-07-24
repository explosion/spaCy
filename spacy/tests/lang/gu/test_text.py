# coding: utf-8
from __future__ import unicode_literals

import pytest


def test_gu_tokenizer_handlers_long_text(gu_tokenizer):
    text = """પશ્ચિમ ભારતમાં આવેલું ગુજરાત રાજ્ય જે વ્યક્તિઓની માતૃભૂમિ છે"""
    tokens = gu_tokenizer(text)
    assert len(tokens) == 9


@pytest.mark.parametrize(
    "text,length",
    [("ગુજરાતીઓ ખાવાના શોખીન માનવામાં આવે છે", 6), ("ખેતરની ખેડ કરવામાં આવે છે.", 5)],
)
def test_gu_tokenizer_handles_cnts(gu_tokenizer, text, length):
    tokens = gu_tokenizer(text)
    assert len(tokens) == length


@pytest.mark.parametrize(
    "text,match",
    [
        ("10", True),
        ("1", True),
        ("10,000", True),
        ("અઠ્ઠાવન", True),
        ("ઓગણિસ", True),
        ("પાંચસો", True),
        ("આઠસો", True),
        ("1/2", True),
    ],
)
def test_lex_attrs_like_number(gu_tokenizer, text, match):
    tokens = gu_tokenizer(text)
    assert len(tokens) == 1
    assert tokens[0].like_num == match
