from __future__ import unicode_literals

from spacy.en import unhash
from spacy import lex_of
from spacy import en
from spacy.util import utf8open

import pytest
import os
from os import path


HERE = path.dirname(__file__)


@pytest.fixture
def sun_txt():
    loc = path.join(HERE, 'sun.txt')
    return utf8open(loc).read()


def test_tokenize(sun_txt):
    assert len(sun_txt) != 0
    tokens = en.tokenize(sun_txt)
    assert True
