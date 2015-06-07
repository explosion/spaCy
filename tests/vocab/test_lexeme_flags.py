from __future__ import unicode_literals

import pytest

from spacy.en import English
from spacy.en.attrs import *


@pytest.fixture
def EN():
    return English()


def test_is_alpha(EN):
    the = EN.vocab['the']
    assert the.flags & (1 << IS_ALPHA)
    year = EN.vocab['1999']
    assert not year.flags & (1 << IS_ALPHA)
    mixed = EN.vocab['hello1']
    assert not mixed.flags & (1 << IS_ALPHA)


def test_is_digit(EN):
    the = EN.vocab['the']
    assert not the.flags & (1 << IS_DIGIT)
    year = EN.vocab['1999']
    assert year.flags & (1 << IS_DIGIT)
    mixed = EN.vocab['hello1']
    assert not mixed.flags & (1 << IS_DIGIT)
