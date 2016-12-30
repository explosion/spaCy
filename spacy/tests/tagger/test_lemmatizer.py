# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import io
import pickle
import pathlib

from spacy.lemmatizer import Lemmatizer, read_index, read_exc
from spacy import util

import pytest


@pytest.fixture
def path():
    if 'SPACY_DATA' in os.environ:
        return pathlib.Path(os.environ['SPACY_DATA'])
    else:
        return util.match_best_version('en', None, util.get_data_path())


@pytest.fixture
def lemmatizer(path):
    if path is not None:
        return Lemmatizer.load(path)
    else:
        return None


def test_read_index(path):
    if path is not None:
        with (path / 'wordnet' / 'index.noun').open() as file_:
            index = read_index(file_)
        assert 'man' in index
        assert 'plantes' not in index
        assert 'plant' in index


def test_read_exc(path):
    if path is not None:
        with (path / 'wordnet' / 'verb.exc').open() as file_:
            exc = read_exc(file_)
        assert exc['was'] == ('be',)


def test_noun_lemmas(lemmatizer):
    if lemmatizer is None:
        return None
    do = lemmatizer.noun

    assert do('aardwolves') == set(['aardwolf'])
    assert do('aardwolf') == set(['aardwolf'])
    assert do('planets') == set(['planet'])
    assert do('ring') == set(['ring'])
    assert do('axes') == set(['axis', 'axe', 'ax'])


def test_base_form_dive(lemmatizer):
    if lemmatizer is None:
        return None

    do = lemmatizer.noun
    assert do('dive', {'number': 'sing'}) == set(['dive'])
    assert do('dive', {'number': 'plur'}) == set(['diva'])


def test_base_form_saw(lemmatizer):
    if lemmatizer is None:
        return None

    do = lemmatizer.verb
    assert do('saw', {'verbform': 'past'}) == set(['see'])


def test_smart_quotes(lemmatizer):
    if lemmatizer is None:
        return None

    do = lemmatizer.punct
    assert do('“') == set(['"'])
    assert do('“') == set(['"'])


def test_pickle_lemmatizer(lemmatizer):
    if lemmatizer is None:
        return None

    file_ = io.BytesIO()
    pickle.dump(lemmatizer, file_)

    file_.seek(0)

    loaded = pickle.load(file_)
