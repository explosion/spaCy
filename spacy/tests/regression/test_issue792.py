# coding: utf-8
from __future__ import unicode_literals

import pytest


@pytest.mark.parametrize('text', ["This is a string ", "This is a string\u0020"])
def test_issue792(en_tokenizer, text):
    """Test for Issue #792: Trailing whitespace is removed after tokenization."""
    doc = en_tokenizer(text)
    assert ''.join([token.text_with_ws for token in doc]) == text


@pytest.mark.parametrize('text', ["This is a string", "This is a string\n"])
def test_control_issue792(en_tokenizer, text):
    """Test base case for Issue #792: Non-trailing whitespace"""
    doc = en_tokenizer(text)
    assert ''.join([token.text_with_ws for token in doc]) == text
