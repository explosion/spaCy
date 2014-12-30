from __future__ import unicode_literals

from spacy.en import English
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
    nlp = English()
    assert len(sun_txt) != 0
    tokens = nlp(sun_txt)
    assert True
