from __future__ import unicode_literals

from spacy.en.lemmatizer import Lemmatizer, read_index, read_exc
from spacy.en import LOCAL_DATA_DIR
from os import path

import pytest


def test_read_index():
    wn = path.join(LOCAL_DATA_DIR, 'wordnet')
    index = read_index(path.join(wn, 'index.noun'))
    assert 'man' in index
    assert 'plantes' not in index
    assert 'plant' in index


def test_read_exc():
    wn = path.join(LOCAL_DATA_DIR, 'wordnet')
    exc = read_exc(path.join(wn, 'verb.exc'))
    assert exc['was'] == ('be',)


@pytest.fixture
def lemmatizer():
    return Lemmatizer(path.join(LOCAL_DATA_DIR, 'wordnet'), 0, 0, 0)


def test_noun_lemmas(lemmatizer):
    do = lemmatizer.noun

    assert do('aardwolves') == set(['aardwolf'])
    assert do('aardwolf') == set(['aardwolf'])
    assert do('planets') == set(['planet'])
    assert do('ring') == set(['ring'])
    assert do('axes') == set(['axis', 'axe', 'ax'])
