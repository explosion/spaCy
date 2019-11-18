# coding: utf-8
from __future__ import unicode_literals

import pytest


# fmt: off
TOKENIZER_TESTS = [
    ("作为语言而言，为世界使用人数最多的语言，目前世界有五分之一人口做为母语。",
        ['作为', '语言', '而言', '，', '为', '世界', '使用', '人', '数最多',
         '的', '语言', '，', '目前', '世界', '有', '五分之一', '人口', '做',
         '为', '母语', '。']),
]
# fmt: on


@pytest.mark.parametrize("text,expected_tokens", TOKENIZER_TESTS)
def test_zh_tokenizer(zh_tokenizer, text, expected_tokens):
    zh_tokenizer.use_jieba = False
    tokens = [token.text for token in zh_tokenizer(text)]
    assert tokens == list(text)

    zh_tokenizer.use_jieba = True
    tokens = [token.text for token in zh_tokenizer(text)]
    assert tokens == expected_tokens


def test_extra_spaces(zh_tokenizer):
    # note: three spaces after "I"
    tokens = zh_tokenizer("I   like cheese.")
    assert tokens[1].orth_ == "  "
