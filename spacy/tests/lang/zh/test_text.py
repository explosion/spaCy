# coding: utf-8
from __future__ import unicode_literals


import pytest


@pytest.mark.parametrize(
    "text,match",
    [
        ("10", True),
        ("1", True),
        ("999.0", True),
        ("一", True),
        ("二", True),
        ("〇", True),
        ("十一", True),
        ("狗", False),
        (",", False),
    ],
)
def test_lex_attrs_like_number(zh_tokenizer_jieba, text, match):
    tokens = zh_tokenizer_jieba(text)
    assert len(tokens) == 1
    assert tokens[0].like_num == match
