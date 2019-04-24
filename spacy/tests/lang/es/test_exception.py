# coding: utf-8
from __future__ import unicode_literals

import pytest


@pytest.mark.parametrize(
    "text,lemma",
    [
        ("aprox.", "aproximadamente"),
        ("esq.", "esquina"),
        ("pág.", "página"),
        ("p.ej.", "por ejemplo"),
    ],
)
def test_es_tokenizer_handles_abbr(es_tokenizer, text, lemma):
    tokens = es_tokenizer(text)
    assert len(tokens) == 1
    assert tokens[0].lemma_ == lemma


def test_es_tokenizer_handles_exc_in_text(es_tokenizer):
    text = "Mariano Rajoy ha corrido aprox. medio kilómetro"
    tokens = es_tokenizer(text)
    assert len(tokens) == 7
    assert tokens[4].text == "aprox."
    assert tokens[4].lemma_ == "aproximadamente"
