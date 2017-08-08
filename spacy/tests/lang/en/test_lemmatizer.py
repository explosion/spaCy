# coding: utf-8
from __future__ import unicode_literals

import pytest


@pytest.fixture
def en_lemmatizer(EN):
    return EN.Defaults.create_lemmatizer()


@pytest.mark.models('en')
@pytest.mark.parametrize('text,lemmas', [("aardwolves", ["aardwolf"]),
                                         ("aardwolf", ["aardwolf"]),
                                         ("planets", ["planet"]),
                                         ("ring", ["ring"]),
                                         ("axes", ["axis", "axe", "ax"])])
def test_en_lemmatizer_noun_lemmas(en_lemmatizer, text, lemmas):
    assert en_lemmatizer.noun(text) == set(lemmas)


@pytest.mark.xfail
@pytest.mark.models('en')
def test_en_lemmatizer_base_forms(en_lemmatizer):
    assert en_lemmatizer.noun('dive', {'number': 'sing'}) == set(['dive'])
    assert en_lemmatizer.noun('dive', {'number': 'plur'}) == set(['diva'])


@pytest.mark.models('en')
def test_en_lemmatizer_base_form_verb(en_lemmatizer):
    assert en_lemmatizer.verb('saw', {'verbform': 'past'}) == set(['see'])


@pytest.mark.models('en')
def test_en_lemmatizer_punct(en_lemmatizer):
    assert en_lemmatizer.punct('“') == set(['"'])
    assert en_lemmatizer.punct('“') == set(['"'])


@pytest.mark.models('en')
def test_en_lemmatizer_lemma_assignment(EN):
    text = "Bananas in pyjamas are geese."
    doc = EN.make_doc(text)
    EN.tensorizer(doc)
    assert all(t.lemma_ == '' for t in doc)
    EN.tagger(doc)
    assert all(t.lemma_ != '' for t in doc)
