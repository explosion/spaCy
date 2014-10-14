from __future__ import unicode_literals

import pytest

from spacy.en import EN


def test_hyphen():
    tokens = EN.tokenize('best-known')
    assert len(tokens) == 3


def test_period():
    tokens = EN.tokenize('best.Known')
    assert len(tokens) == 3
    tokens = EN.tokenize('zombo.com')
    assert len(tokens) == 1
