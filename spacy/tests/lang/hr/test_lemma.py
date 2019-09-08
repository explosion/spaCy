# coding: utf-8
from __future__ import unicode_literals

import pytest


@pytest.mark.parametrize(
    "string,lemma",
    [
        ("trčao", "trčati"),
        ("adekvatnim", "adekvatan"),
        ("dekontaminacijama", "dekontaminacija"),
        ("filologovih", "filologov"),
        ("je", "biti"),
        ("se", "sebe"),
    ],
)
def test_hr_lemmatizer_lookup_assigns(hr_tokenizer, string, lemma):
    tokens = hr_tokenizer(string)
    assert tokens[0].lemma_ == lemma
