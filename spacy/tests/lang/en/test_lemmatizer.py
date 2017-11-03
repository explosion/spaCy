# coding: utf-8
from __future__ import unicode_literals

import pytest
from ....tokens.doc import Doc


@pytest.fixture
def en_lemmatizer(EN):
    return EN.Defaults.create_lemmatizer()

@pytest.mark.models('en')
def test_doc_lemmatization(EN):
    doc = Doc(EN.vocab, words=['bleed'])
    doc[0].tag_ = 'VBP'
    assert doc[0].lemma_ == 'bleed'

@pytest.mark.models('en')
@pytest.mark.parametrize('text,lemmas', [("aardwolves", ["aardwolf"]),
                                         ("aardwolf", ["aardwolf"]),
                                         ("planets", ["planet"]),
                                         ("ring", ["ring"]),
                                         ("axes", ["axis", "axe", "ax"])])
def test_en_lemmatizer_noun_lemmas(en_lemmatizer, text, lemmas):
    assert en_lemmatizer.noun(text) == lemmas


@pytest.mark.models('en')
@pytest.mark.parametrize('text,lemmas', [("bleed", ["bleed"]),
                                         ("feed", ["feed"]),
                                         ("need", ["need"]),
                                         ("ring", ["ring"])])
def test_en_lemmatizer_noun_lemmas(en_lemmatizer, text, lemmas):
    # Cases like this are problematic -- not clear what we should do to resolve
    # ambiguity?
    # ("axes", ["ax", "axes", "axis"])])
    assert en_lemmatizer.noun(text) == lemmas


@pytest.mark.xfail
@pytest.mark.models('en')
def test_en_lemmatizer_base_forms(en_lemmatizer):
    assert en_lemmatizer.noun('dive', {'number': 'sing'}) == ['dive']
    assert en_lemmatizer.noun('dive', {'number': 'plur'}) == ['diva']


@pytest.mark.models('en')
def test_en_lemmatizer_base_form_verb(en_lemmatizer):
    assert en_lemmatizer.verb('saw', {'verbform': 'past'}) == ['see']


@pytest.mark.models('en')
def test_en_lemmatizer_punct(en_lemmatizer):
    assert en_lemmatizer.punct('“') == ['"']
    assert en_lemmatizer.punct('“') == ['"']


@pytest.mark.models('en')
def test_en_lemmatizer_lemma_assignment(EN):
    text = "Bananas in pyjamas are geese."
    doc = EN.make_doc(text)
    EN.tagger(doc)
    assert all(t.lemma_ != '' for t in doc)
