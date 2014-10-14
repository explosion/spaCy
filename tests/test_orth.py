from __future__ import unicode_literals

import pytest

import spacy.word
from spacy.en import EN
from spacy.lexeme import *


@pytest.fixture
def C3P0():
    return EN.lexicon.lookup("C3P0")


def test_shape(C3P0):
    assert C3P0.string_view(LexStr_shape) == "XdXd"


def test_length():
    t = EN.lexicon.lookup('the')
    assert t.length == 3
    t = EN.lexicon.lookup("n't")
    assert t.length == 3
    t = EN.lexicon.lookup("'s")
    assert t.length == 2
    t = EN.lexicon.lookup('Xxxx')
    assert t.length == 4
