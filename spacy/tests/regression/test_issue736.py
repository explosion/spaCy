# coding: utf-8
from __future__ import unicode_literals

import pytest


@pytest.mark.parametrize('text,number', [("7am", "7"), ("11p.m.", "11")])
def test_issue736(en_tokenizer, text, number):
    """Test that times like "7am" are tokenized correctly and that numbers are converted to string."""
    tokens = en_tokenizer(text)
    assert len(tokens) == 2
    assert tokens[0].text == number
