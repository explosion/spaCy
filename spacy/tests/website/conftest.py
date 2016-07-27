from __future__ import unicode_literals
import pytest
import os


@pytest.fixture(scope='session')
def nlp():
    from spacy.en import English
    if os.environ.get('SPACY_DATA'):
        data_dir = os.environ.get('SPACY_DATA')
    else:
        data_dir = None
    return English(data_dir=data_dir)


@pytest.fixture()
def doc(nlp):
    return nlp('Hello, world. Here are two sentences.')
