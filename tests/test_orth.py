from __future__ import unicode_literals

import pytest

from spacy.en import lookup, unhash
import spacy.word


@pytest.fixture
def C3P0():
    return lookup("C3P0")


def test_shape(C3P0):
    # TODO: Fix this
    assert unhash(C3P0.get_view(2)) == "XdXd"


def test_length():
    t = lookup('the')
    assert t.length == 3
    t = lookup("n't")
    assert t.length == 3
    t = lookup("'s")
    assert t.length == 2
    t = lookup('Xxxx')
    assert t.length == 4
