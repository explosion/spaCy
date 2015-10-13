# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import StringIO
import pickle

from spacy.lemmatizer import Lemmatizer, read_index, read_exc
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
    return Lemmatizer.from_dir(path.join(LOCAL_DATA_DIR))


def test_noun_lemmas(lemmatizer):
    do = lemmatizer.noun

    assert do('aardwolves') == set(['aardwolf'])
    assert do('aardwolf') == set(['aardwolf'])
    assert do('planets') == set(['planet'])
    assert do('ring') == set(['ring'])
    assert do('axes') == set(['axis', 'axe', 'ax'])


def test_smart_quotes(lemmatizer):
    do = lemmatizer.punct
    assert do('“') == set(['"'])
    assert do('“') == set(['"'])


def test_pickle_lemmatizer(lemmatizer):
    file_ = StringIO.StringIO()
    pickle.dump(lemmatizer, file_)

    file_.seek(0)
    
    loaded = pickle.load(file_)
