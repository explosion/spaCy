# coding: utf-8
from __future__ import unicode_literals

import pytest


@pytest.mark.parametrize("text", ["Ahmet'te", "Istanbul'da"])
def test_tr_tokenizer_handles_apostropher(tr_tokenizer, text):
    tokens = tr_tokenizer(text)
    assert len(tokens) == 1


@pytest.mark.parametrize("text", ["5'te", "6'da"])
def test_tr_tokenizer_handles_num_apostropher(tr_tokenizer, text):
    tokens = tr_tokenizer(text)
    assert len(tokens) == 1


@pytest.mark.parametrize("text", ["Dr.", "Yrd.Doç."])
def test_tr_tokenizer_handles_abbr(tr_tokenizer, text):
    tokens = tr_tokenizer(text)
    assert len(tokens) == 1


def test_tr_tokenizer_handles_exc_in_text(tr_tokenizer):
    text = "Dr. Murat Bey ile görüştüm."
    tokens = tr_tokenizer(text)
    assert len(tokens) == 6
    assert tokens[0].text == "Dr."
    assert tokens[0].lemma_ == "doktor"


@pytest.mark.parametrize("text", ["Prof.'un", "Böl.'nde"])
def test_tr_tokenizer_handles_abbr_cased(tr_tokenizer, text):
    tokens = tr_tokenizer(text)
    assert len(tokens) == 1


@pytest.mark.parametrize("text", ["6.", "7.", "77.", "712."])
def test_tr_tokenizer_handles_alone_ordinals(tr_tokenizer, text):
    tokens = tr_tokenizer(text)
    assert len(tokens) == 1


@pytest.mark.parametrize("text", ["IV.", "V.", "VI.", "XX."])
def test_tr_tokenizer_handles_alone_roman_ordinals(tr_tokenizer, text):
    tokens = tr_tokenizer(text)
    assert len(tokens) == 1


def test_tr_tokenizer_handles_ordinal_num_in_text(tr_tokenizer):
    text = "Yarışta 6. oldum."
    tokens = tr_tokenizer(text)
    for token in tokens:
        print(token)
    assert len(tokens) == 4
    assert tokens[1].text == "6."


def test_tr_tokenizer_handles_roman_ordinal_num_in_text(tr_tokenizer):
    text = "Kitap IV. Murat hakkında."
    tokens = tr_tokenizer(text)
    for token in tokens:
        print(token)
    assert len(tokens) == 5
    assert tokens[1].text == "IV."


def test_tr_tokenizer_handles_long_ordinal_num_in_text(tr_tokenizer):
    text = "Yarışta 438547745. oldum."
    tokens = tr_tokenizer(text)
    assert len(tokens) == 4
    assert tokens[1].text == "438547745."


def test_tr_tokenizer_handles_cardinal_at_end_of_sentence(tr_tokenizer):
    text = "Bana söylediği sayı 6."
    tokens = tr_tokenizer(text)
    assert len(tokens) == 5
    assert tokens[-1].text == "."
    assert tokens[-2].text == "6"


def test_tr_tokenizer_handles_ordinal_and_apostophe(tr_tokenizer):
    text = "Saat 6'da buluşalım."  # We'll meet at 6 o'clock tomorrow.
    tokens = tr_tokenizer(text)
    assert len(tokens) == 4
    assert tokens[1].text == "6'da"  # six dative

def test_tr_tokenizer_handles_ordinal_and_apostophe_with_period(tr_tokenizer):
    text = "Saat 6'ydı."  # We'll meet at 6 o'clock tomorrow.
    tokens = tr_tokenizer(text)
    assert len(tokens) == 3
    assert tokens[-1].text == "."  
    assert tokens[-2].text == "6'ydı"  # six dative
