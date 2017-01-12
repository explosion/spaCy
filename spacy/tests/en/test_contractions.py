# coding: utf-8
"""Test that tokens are created correctly for contractions."""


from __future__ import unicode_literals

import pytest


def test_tokenizer_handles_basic_contraction(en_tokenizer):
    text = "don't giggle"
    tokens = en_tokenizer(text)
    assert len(tokens) == 3
    assert tokens[1].text == "n't"
    text = "i said don't!"
    tokens = en_tokenizer(text)
    assert len(tokens) == 5
    assert tokens[4].text == "!"


@pytest.mark.parametrize('text', ["`ain't", '''"isn't''', "can't!"])
def test_tokenizer_handles_basic_contraction_punct(en_tokenizer, text):
    tokens = en_tokenizer(text)
    assert len(tokens) == 3


@pytest.mark.parametrize('text_poss,text', [("Robin's", "Robin"), ("Alexis's", "Alexis")])
def test_tokenizer_handles_poss_contraction(en_tokenizer, text_poss, text):
    tokens = en_tokenizer(text_poss)
    assert len(tokens) == 2
    assert tokens[0].text == text
    assert tokens[1].text == "'s"


@pytest.mark.parametrize('text', ["schools'", "Alexis'"])
def test_tokenizer_splits_trailing_apos(en_tokenizer, text):
    tokens = en_tokenizer(text)
    assert len(tokens) == 2
    assert tokens[0].text == text.split("'")[0]
    assert tokens[1].text == "'"


@pytest.mark.parametrize('text', ["'em", "nothin'", "ol'"])
def text_tokenizer_doesnt_split_apos_exc(en_tokenizer, text):
    tokens = en_tokenizer(text)
    assert len(tokens) == 1
    assert tokens[0].text == text


@pytest.mark.parametrize('text', ["we'll", "You'll", "there'll"])
def test_tokenizer_handles_ll_contraction(en_tokenizer, text):
    tokens = en_tokenizer(text)
    assert len(tokens) == 2
    assert tokens[0].text == text.split("'")[0]
    assert tokens[1].text == "'ll"
    assert tokens[1].lemma_ == "will"


@pytest.mark.parametrize('text_lower,text_title', [("can't", "Can't"), ("ain't", "Ain't")])
def test_tokenizer_handles_capitalization(en_tokenizer, text_lower, text_title):
    tokens_lower = en_tokenizer(text_lower)
    tokens_title = en_tokenizer(text_title)
    assert tokens_title[0].text == tokens_lower[0].text.title()
    assert tokens_lower[0].text == tokens_title[0].text.lower()
    assert tokens_lower[1].text == tokens_title[1].text


@pytest.mark.parametrize('pron', ["I", "You", "He", "She", "It", "We", "They"])
@pytest.mark.parametrize('contraction', ["'ll", "'d"])
def test_tokenizer_keeps_title_case(en_tokenizer, pron, contraction):
    tokens = en_tokenizer(pron + contraction)
    assert tokens[0].text == pron
    assert tokens[1].text == contraction


@pytest.mark.parametrize('exc', ["Ill", "ill", "Hell", "hell", "Well", "well"])
def test_tokenizer_excludes_ambiguous(en_tokenizer, exc):
    tokens = en_tokenizer(exc)
    assert len(tokens) == 1


@pytest.mark.parametrize('wo_punct,w_punct', [("We've", "``We've"), ("couldn't", "couldn't)")])
def test_tokenizer_splits_defined_punct(en_tokenizer, wo_punct, w_punct):
    tokens = en_tokenizer(wo_punct)
    assert len(tokens) == 2
    tokens = en_tokenizer(w_punct)
    assert len(tokens) == 3
