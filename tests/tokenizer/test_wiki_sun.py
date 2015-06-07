from __future__ import unicode_literals

from spacy.util import utf8open

import pytest
from os import path


HERE = path.dirname(__file__)


@pytest.fixture
def sun_txt():
    loc = path.join(HERE, 'sun.txt')
    return utf8open(loc).read()


def test_tokenize(sun_txt, EN):
    assert len(sun_txt) != 0
    tokens = nlp(sun_txt)
    assert len(tokens) > 100
