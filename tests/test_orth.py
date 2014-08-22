from __future__ import unicode_literals

import pytest

from spacy.en import lookup, unhash

from spacy.en import lex_of, shape_of, norm_of, first_of, length_of

@pytest.fixture
def C3P0():
    return lookup("C3P0")


def test_shape(C3P0):
    assert unhash(shape_of(C3P0)) == "XdXd"


def test_length():
    t = lookup('the')
    assert length_of(t) == 3
    #t = lookup('')
    #assert length_of(t) == 0
    t = lookup("n't")
    assert length_of(t) == 3
    t = lookup("'s")
    assert length_of(t) == 2
    t = lookup('Xxxx')
    assert length_of(t) == 4
