# coding: utf-8
"""Test that tokens are created correctly for whitespace."""


from __future__ import unicode_literals

import pytest


@pytest.mark.parametrize('text', ["hello possums"])
def test_tokenizer_splits_single_space(en_tokenizer, text):
    tokens = en_tokenizer(text)
    assert len(tokens) == 2


@pytest.mark.parametrize('text', ["hello  possums"])
def test_tokenizer_splits_double_space(en_tokenizer, text):
    tokens = en_tokenizer(text)
    assert len(tokens) == 3
    assert tokens[1].text == " "


@pytest.mark.parametrize('text', ["two spaces after this  "])
def test_tokenizer_handles_double_trainling_ws(en_tokenizer, text):
    tokens = en_tokenizer(text)
    assert repr(tokens.text_with_ws) == repr(text)


@pytest.mark.parametrize('text', ["hello\npossums"])
def test_tokenizer_splits_newline(en_tokenizer, text):
    tokens = en_tokenizer(text)
    assert len(tokens) == 3
    assert tokens[1].text == "\n"


@pytest.mark.parametrize('text', ["hello \npossums"])
def test_tokenizer_splits_newline_space(en_tokenizer, text):
    tokens = en_tokenizer('hello \npossums')
    assert len(tokens) == 3


@pytest.mark.parametrize('text', ["hello  \npossums"])
def test_tokenizer_splits_newline_double_space(en_tokenizer, text):
    tokens = en_tokenizer(text)
    assert len(tokens) == 3


@pytest.mark.parametrize('text', ["hello \n possums"])
def test_tokenizer_splits_newline_space_wrap(en_tokenizer, text):
    tokens = en_tokenizer(text)
    assert len(tokens) == 3
