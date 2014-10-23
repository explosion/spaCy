from __future__ import unicode_literals

import pytest

from spacy.en import *
from spacy.lexeme import *


def test_is_alpha():
    the = EN.lexicon.lookup('the')
    assert the['flags'] & (1 << IS_ALPHA)
    year = EN.lexicon.lookup('1999')
    assert not year['flags'] & (1 << IS_ALPHA)
    mixed = EN.lexicon.lookup('hello1')
    assert not mixed['flags'] & (1 << IS_ALPHA)


def test_is_digit():
    the = EN.lexicon.lookup('the')
    assert not the['flags'] & (1 << IS_DIGIT)
    year = EN.lexicon.lookup('1999')
    assert year['flags'] & (1 << IS_DIGIT)
    mixed = EN.lexicon.lookup('hello1')
    assert not mixed['flags'] & (1 << IS_DIGIT)
