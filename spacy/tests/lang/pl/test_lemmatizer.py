# coding: utf-8
from __future__ import unicode_literals

import pytest
from spacy.lang.pl import Polish

lookup_lemmatization_cases = [
    ("ciężkozbrojnego", "ciężkozbrojny", "adj"),
    ("ciężkozbrojnymi", "ciężkozbrojny", "adj"),
    ("klinicznemu", "kliniczny", "adv"),
    ("obrończynią", "obrończyni", "noun"),
    ("robię", "robić", "verb"),
    ("jagiellońskiego", "jagielloński", "part"),
    ("Morawieckiego", "morawiecki", "noun")

]

oov_lemmatization_cases = [
    ("popielgrzymiłem", "popielgrzymić", "verb")
]

@pytest.fixture
def pl_lemmatizer():
    return Polish.Defaults.create_lemmatizer()


@pytest.mark.parametrize("text,lemma,pos", lookup_lemmatization_cases)
def test_pl_lemmatizer_lookup(pl_lemmatizer, text, lemma, pos):
    lemmas_pred = pl_lemmatizer(text, pos)
    assert lemma == sorted(lemmas_pred)[0]


@pytest.mark.parametrize("text,lemma,pos", oov_lemmatization_cases)
def test_pl_lemmatizer_oov(pl_lemmatizer, text, lemma, pos):
    lemmas_pred = pl_lemmatizer(text, pos)
    assert lemma in lemmas_pred
