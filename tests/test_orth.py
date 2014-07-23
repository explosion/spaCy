from __future__ import unicode_literals

import pytest

from spacy.en import lookup, unhash

from spacy.lexeme import sic_of, lex_of, norm_of, shape_of, first_of
from spacy.lexeme import shape_of

@pytest.fixture
def C3P0():
    return lookup("C3P0")


def test_shape(C3P0):
    assert unhash(shape_of(C3P0)) == "XdXd"
