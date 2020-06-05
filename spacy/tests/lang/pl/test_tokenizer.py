# coding: utf8
from __future__ import unicode_literals

import pytest

DOT_TESTS = [
    ("tel.", ["tel", "."]),
    ("0 zł 99 gr", ["0", "zł", "99", "gr"]),
]

HYPHEN_TESTS = [
    ("cztero-", ["cztero-"]),
    ("jedno-", ["jedno-"]),
    ("dwu-", ["dwu-"]),
    ("trzy-", ["trzy-"]),
]


TESTCASES = DOT_TESTS + HYPHEN_TESTS


@pytest.mark.parametrize("text,expected_tokens", TESTCASES)
def test_tokenizer_handles_testcases(pl_tokenizer, text, expected_tokens):
    tokens = pl_tokenizer(text)
    token_list = [token.text for token in tokens if not token.is_space]
    assert expected_tokens == token_list
