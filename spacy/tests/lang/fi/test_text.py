# coding: utf-8
from __future__ import unicode_literals

import pytest


@pytest.mark.parametrize(
    "text,match",
    [
        ("10", True),
        ("1", True),
        ("10000", True),
        ("10,00", True),
        ("-999,0", True),
        ("yksi", True),
        ("kolmetoista", True),
        ("viisikymmentä", True),
        ("tuhat", True),
        ("1/2", True),
        ("hevonen", False),
        (",", False),
    ],
)
def test_fi_lex_attrs_like_number(fi_tokenizer, text, match):
    tokens = fi_tokenizer(text)
    assert len(tokens) == 1
    assert tokens[0].like_num == match
