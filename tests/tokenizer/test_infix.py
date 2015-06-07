from __future__ import unicode_literals

import pytest

from spacy.en import English

EN = English()

def test_hyphen():
    tokens = EN.tokenizer('best-known')
    assert len(tokens) == 3


def test_period():
    tokens = EN.tokenizer('best.Known')
    assert len(tokens) == 3
    tokens = EN.tokenizer('zombo.com')
    assert len(tokens) == 1
