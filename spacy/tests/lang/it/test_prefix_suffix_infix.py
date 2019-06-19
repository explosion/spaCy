# coding: utf-8
from __future__ import unicode_literals

import pytest


@pytest.mark.parametrize(
    "text,expected_tokens", [("c'è", ["c'", "è"]), ("l'ha", ["l'", "ha"])]
)
def test_contractions(it_tokenizer, text, expected_tokens):
    """ Test that the contractions are split into two tokens"""
    tokens = it_tokenizer(text)
    assert len(tokens) == 2
    assert [t.text for t in tokens] == expected_tokens
