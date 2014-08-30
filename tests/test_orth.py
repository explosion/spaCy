from __future__ import unicode_literals

import pytest

import spacy.word
from spacy import en

EN = en.EN


@pytest.fixture
def C3P0():
    return EN.lookup("C3P0")


def test_shape(C3P0):
    assert C3P0.string_view(en.SHAPE) == "XdXd"


def test_length():
    t = EN.lookup('the')
    assert t.length == 3
    t = EN.lookup("n't")
    assert t.length == 3
    t = EN.lookup("'s")
    assert t.length == 2
    t = EN.lookup('Xxxx')
    assert t.length == 4
