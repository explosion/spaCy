# coding: utf-8
from __future__ import unicode_literals

from ...lemmatizer import read_index, read_exc

import pytest


@pytest.mark.models
@pytest.mark.parametrize('text,lemmas', [("aardwolves", ["aardwolf"]),
                                         ("aardwolf", ["aardwolf"]),
                                         ("planets", ["planet"]),
                                         ("ring", ["ring"]),
                                         ("axes", ["axis", "axe", "ax"])])
def test_tagger_lemmatizer_noun_lemmas(lemmatizer, text, lemmas):
    if lemmatizer is None:
        return None
    assert lemmatizer.noun(text) == set(lemmas)


@pytest.mark.models
def test_tagger_lemmatizer_base_forms(lemmatizer):
    if lemmatizer is None:
        return None
    assert lemmatizer.noun('dive', {'number': 'sing'}) == set(['dive'])
    assert lemmatizer.noun('dive', {'number': 'plur'}) == set(['diva'])


@pytest.mark.models
def test_tagger_lemmatizer_base_form_verb(lemmatizer):
    if lemmatizer is None:
        return None
    assert lemmatizer.verb('saw', {'verbform': 'past'}) == set(['see'])


@pytest.mark.models
def test_tagger_lemmatizer_punct(lemmatizer):
    if lemmatizer is None:
        return None
    assert lemmatizer.punct('“') == set(['"'])
    assert lemmatizer.punct('“') == set(['"'])


@pytest.mark.models
def test_tagger_lemmatizer_read_index(path):
    if path is not None:
        with (path / 'wordnet' / 'index.noun').open() as file_:
            index = read_index(file_)
        assert 'man' in index
        assert 'plantes' not in index
        assert 'plant' in index


@pytest.mark.models
@pytest.mark.parametrize('text,lemma', [("was", "be")])
def test_tagger_lemmatizer_read_exc(path, text, lemma):
    if path is not None:
        with (path / 'wordnet' / 'verb.exc').open() as file_:
            exc = read_exc(file_)
        assert exc[text] == (lemma,)


@pytest.mark.models
def test_tagger_lemmatizer_lemma_assignment(EN):
    text = "Bananas in pyjamas are geese."
    doc = EN.tokenizer(text)
    assert all(t.lemma_ == '' for t in doc)
    EN.tagger(doc)
    assert all(t.lemma_ != '' for t in doc)
