# coding: utf-8
from __future__ import unicode_literals

import pytest


@pytest.mark.parametrize("tokens,lemmas", [
    (["Galime", "vadinti", "gerovės", "valstybe", ",", "turime", "išvystytą", "socialinę", "apsaugą", ",",
      "sveikatos", "apsaugą", "ir", "prieinamą", "švietimą", "."],
     ["galėti", "vadintas", "gerovė", "valstybė", ",", "turėti", "išvystytas", "socialinis",
      "apsauga", ",", "sveikata", "apsauga", "ir", "prieinamas", "švietimas", "."]),
    (["taip", ",", "uoliai", "tyrinėjau", "ir", "pasirinkau", "geriausią", "variantą", "."],
     ["taip", ",", "uolus", "tyrinėti", "ir", "pasirinkti", "geras", "variantas", "."])])
def test_lt_lemmatizer(lt_lemmatizer, tokens, lemmas):
    assert lemmas == [lt_lemmatizer.lookup(token) for token in tokens]
