from __future__ import unicode_literals

import pytest

from spacy.en import English


#def test_hyphen():
#    tokens = EN.tokenize('best-known')
#    assert len(tokens) == 3


def test_period():
    EN = English()
    tokens = EN('best.Known')
    assert len(tokens) == 3
    tokens = EN('zombo.com')
    assert len(tokens) == 1
