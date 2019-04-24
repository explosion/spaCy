# coding: utf8
from __future__ import unicode_literals

import pytest


@pytest.mark.parametrize(
    "text,expected_tokens", [("คุณรักผมไหม", ["คุณ", "รัก", "ผม", "ไหม"])]
)
def test_th_tokenizer(th_tokenizer, text, expected_tokens):
    tokens = [token.text for token in th_tokenizer(text)]
    assert tokens == expected_tokens
