# coding: utf-8
from __future__ import unicode_literals

import pytest


@pytest.mark.parametrize(
    "string,lemma",
    [
        ("Abgehängten", "Abgehängte"),
        ("engagierte", "engagieren"),
        ("schließt", "schließen"),
        ("vorgebenden", "vorgebend"),
        ("die", "der"),
        ("Die", "der"),
    ],
)
def test_de_lemmatizer_lookup_assigns(de_tokenizer, string, lemma):
    tokens = de_tokenizer(string)
    assert tokens[0].lemma_ == lemma
