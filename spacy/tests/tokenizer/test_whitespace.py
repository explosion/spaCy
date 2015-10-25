"""Test that tokens are created correctly for whitespace."""
from __future__ import unicode_literals

import pytest


def test_single_space(en_tokenizer):
    tokens = en_tokenizer('hello possums')
    assert len(tokens) == 2


def test_double_space(en_tokenizer):
    tokens = en_tokenizer('hello  possums')
    assert len(tokens) == 3
    assert tokens[1].orth_ == ' '


def test_newline(en_tokenizer):
    tokens = en_tokenizer('hello\npossums')
    assert len(tokens) == 3


def test_newline_space(en_tokenizer):
    tokens = en_tokenizer('hello \npossums')
    assert len(tokens) == 3


def test_newline_double_space(en_tokenizer):
    tokens = en_tokenizer('hello  \npossums')
    assert len(tokens) == 3


def test_newline_space_wrap(en_tokenizer):
    tokens = en_tokenizer('hello \n possums')
    assert len(tokens) == 3
