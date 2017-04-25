# coding: utf-8

from __future__ import unicode_literals

import pytest

@pytest.mark.xfail
def test_lemmatizer_(fr_tokenizer):
    text = "Je suis allé au mois de janv. aux prud’hommes."
    tokens = fr_tokenizer(text)
    assert len(tokens) == 10
    assert tokens[2].lemma_ == "aller"

@pytest.mark.xfail
def test_tokenizer_handles_exc_in_text_2(fr_tokenizer):
    text = "Je dois manger ce soir"
    tokens = fr_tokenizer(text)
    assert len(tokens) == 11
    assert tokens[1].lemma_ == "devoir"


@pytest.mark.xfail
def test_tokenizer_handles_exc_in_text_2(fr_tokenizer):
    text = "Je dois manger ce soir"
    tokens = fr_tokenizer(text)
    assert len(tokens) == 11
    assert tokens[1].lemma_ == "devoir"

@pytest.mark.xfail
def test_tokenizer_handles_exc_in_text_2(fr_tokenizer):
    # This one is tricky because notes is a NOUN and can be a VERB
    text = "Nous validerons vos notes plus tard"
    tokens = fr_tokenizer(text)
    assert len(tokens) == 11
    assert tokens[1].lemma_ == "valider"
    assert tokens[3].lemma_ == "notes"