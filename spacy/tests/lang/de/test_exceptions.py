# coding: utf-8
from __future__ import unicode_literals

import pytest


@pytest.mark.parametrize("text", ["auf'm", "du's", "über'm", "wir's"])
def test_de_tokenizer_splits_contractions(de_tokenizer, text):
    tokens = de_tokenizer(text)
    assert len(tokens) == 2


@pytest.mark.parametrize("text", ["z.B.", "d.h.", "Jan.", "Dez.", "Chr."])
def test_de_tokenizer_handles_abbr(de_tokenizer, text):
    tokens = de_tokenizer(text)
    assert len(tokens) == 1


def test_de_tokenizer_handles_exc_in_text(de_tokenizer):
    text = "Ich bin z.Zt. im Urlaub."
    tokens = de_tokenizer(text)
    assert len(tokens) == 6
    assert tokens[2].text == "z.Zt."
    assert tokens[2].lemma_ == "zur Zeit"
