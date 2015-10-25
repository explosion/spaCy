from __future__ import unicode_literals

import pytest

def test_hyphen(en_tokenizer):
    tokens = en_tokenizer('best-known')
    assert len(tokens) == 3


def test_numeric_range(en_tokenizer):
    tokens = en_tokenizer('0.1-13.5')
    assert len(tokens) == 3

def test_period(en_tokenizer):
    tokens = en_tokenizer('best.Known')
    assert len(tokens) == 3
    tokens = en_tokenizer('zombo.com')
    assert len(tokens) == 1


def test_ellipsis(en_tokenizer):
    tokens = en_tokenizer('best...Known')
    assert len(tokens) == 3
    tokens = en_tokenizer('best...known')
    assert len(tokens) == 3


def test_email(en_tokenizer):
    tokens = en_tokenizer('hello@example.com')
    assert len(tokens) == 1
    tokens = en_tokenizer('hi+there@gmail.it')
    assert len(tokens) == 1


