# coding: utf-8
from __future__ import unicode_literals

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
def test_tagger_lemmatizer_lemma_assignment(EN):
    text = "Bananas in pyjamas are geese."
    doc = EN.tokenizer(text)
    assert all(t.lemma_ == '' for t in doc)
    EN.tagger(doc)
    assert all(t.lemma_ != '' for t in doc)
