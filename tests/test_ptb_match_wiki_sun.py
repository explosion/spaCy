from __future__ import unicode_literals

from spacy.en import unhash
from spacy import lex_of
from spacy.util import utf8open
from spacy.ptb3 import tokenize, lookup, unhash

import pytest
import os
from os import path


HERE = path.dirname(__file__)


@pytest.fixture
def sun_txt():
    loc = path.join(HERE, 'sun.txt')
    return utf8open(loc).read()


@pytest.fixture
def my_tokens(sun_txt):
    assert len(sun_txt) != 0
    tokens = tokenize(sun_txt)
    return [unhash(lex_of(t)) for t in tokens]


@pytest.fixture
def sed_tokens():
    loc = path.join(HERE, 'sun.tokens')
    return utf8open(loc).read().split()


def test_compare_tokens(my_tokens, sed_tokens):
    me = my_tokens
    sed = sed_tokens
    i = 0
    while i < len(me) and i < len(sed):
        assert me[i] == sed[i]
        i += 1

    assert len(me) == len(sed)



