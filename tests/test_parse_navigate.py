from __future__ import unicode_literals
from os import path
import codecs

from spacy.en import English

import pytest


@pytest.fixture
def sun_text():
    with codecs.open(path.join(path.dirname(__file__), 'sun.txt'), 'r', 'utf8') as file_:
        text = file_.read()
    return text


@pytest.fixture
def nlp():
    return English()


def test_consistency(nlp, sun_text):
    tokens = nlp(sun_text)
    for head in tokens:
        for child in head.lefts:
            assert child.head is head
        for child in head.rights:
            assert child.head is head
