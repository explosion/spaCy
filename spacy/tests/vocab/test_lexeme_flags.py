from __future__ import unicode_literals

import pytest

from spacy.attrs import *


def test_is_alpha(en_vocab):
    the = en_vocab['the']
    assert the.flags & (1 << IS_ALPHA)
    year = en_vocab['1999']
    assert not year.flags & (1 << IS_ALPHA)
    mixed = en_vocab['hello1']
    assert not mixed.flags & (1 << IS_ALPHA)


def test_is_digit(en_vocab):
    the = en_vocab['the']
    assert not the.flags & (1 << IS_DIGIT)
    year = en_vocab['1999']
    assert year.flags & (1 << IS_DIGIT)
    mixed = en_vocab['hello1']
    assert not mixed.flags & (1 << IS_DIGIT)
