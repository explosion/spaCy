# coding: utf-8

from __future__ import unicode_literals

import pytest


@pytest.mark.parametrize(
    "text,lemma",
    [("aprox.", "aproximadament"), ("pàg.", "pàgina"), ("p.ex.", "per exemple")],
)
def test_ca_tokenizer_handles_abbr(ca_tokenizer, text, lemma):
    tokens = ca_tokenizer(text)
    assert len(tokens) == 1
    assert tokens[0].lemma_ == lemma


def test_ca_tokenizer_handles_exc_in_text(ca_tokenizer):
    text = "La Núria i el Pere han vingut aprox. a les 7 de la tarda."
    tokens = ca_tokenizer(text)
    assert len(tokens) == 15
    assert tokens[7].text == "aprox."
    assert tokens[7].lemma_ == "aproximadament"
