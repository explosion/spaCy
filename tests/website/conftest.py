from __future__ import unicode_literals
import pytest


@pytest.fixture(scope='session')
def nlp():
    from spacy.en import English
    return English()


@pytest.fixture()
def doc(nlp):
    return nlp('Hello, world. Here are two sentences.')
