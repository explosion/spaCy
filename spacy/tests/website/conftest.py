from __future__ import unicode_literals
import pytest
import os


@pytest.fixture(scope='session')
def nlp():
    from spacy.en import English
    if os.environ.get('SPACY_DATA'):
        data_dir = os.environ.get('SPACY_DATA')
    else:
        data_dir = True
    return English(path=data_dir)


@pytest.fixture()
def doc(nlp):
    for word in ['Hello', ',', 'world', '.', 'Here', 'are', 'two', 'sentences', '.']:
        _ = nlp.vocab[word]
    return nlp('Hello, world. Here are two sentences.')
