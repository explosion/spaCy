from __future__ import unicode_literals

import pytest

def test_hyphen(en_tokenizer):
    tokens = en_tokenizer('best-known')
    assert len(tokens) == 3


def test_period(en_tokenizer):
    tokens = en_tokenizer('best.Known')
    assert len(tokens) == 3
    tokens = en_tokenizer('zombo.com')
    assert len(tokens) == 1
