# coding: utf-8
from __future__ import unicode_literals

import pytest


@pytest.mark.parametrize(
    "string,lemma",
    [
        ("affaldsgruppernes", "affaldsgruppe"),
        ("detailhandelsstrukturernes", "detailhandelsstruktur"),
        ("kolesterols", "kolesterol"),
        ("åsyns", "åsyn"),
    ],
)
def test_da_lemmatizer_lookup_assigns(da_tokenizer, string, lemma):
    tokens = da_tokenizer(string)
    assert tokens[0].lemma_ == lemma
