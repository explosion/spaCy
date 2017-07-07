# coding: utf-8

from __future__ import unicode_literals

import pytest


@pytest.mark.models
def test_lemmatizer_verb(FR):
    text = "Qu'est-ce que tu fais?"
    tokens = FR(text)
    assert tokens[0].lemma_ == "que"
    assert tokens[1].lemma_ == "être"
    assert tokens[5].lemma_ == "faire"

@pytest.mark.models
@pytest.mark.xfail(reason="sont tagged as AUX")
def test_lemmatizer_noun_verb_2(FR):
    text = "Les abaissements de température sont gênants."
    tokens = FR(text)
    assert tokens[4].lemma_ == "être"

@pytest.mark.models
@pytest.mark.xfail(reason="Costaricienne TAG is PROPN instead of NOUN and spacy don't lemmatize PROPN")
def test_lemmatizer_noun(FR):
    text = "il y a des Costaricienne."
    tokens = FR(text)
    assert tokens[4].lemma_ == "Costaricain"

@pytest.mark.models
def test_lemmatizer_noun_2(FR):
    text = "Les abaissements de température sont gênants."
    tokens = FR(text)
    assert tokens[1].lemma_ == "abaissement"
    assert tokens[5].lemma_ == "gênant"


