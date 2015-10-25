from __future__ import unicode_literals

from spacy.util import utf8open

import pytest
from os import path


HERE = path.dirname(__file__)


@pytest.fixture
def sun_txt():
    loc = path.join(HERE, '..', 'sun.txt')
    return utf8open(loc).read()


def test_tokenize(sun_txt, en_tokenizer):
    assert len(sun_txt) != 0
    tokens = en_tokenizer(sun_txt)
    assert len(tokens) > 100
