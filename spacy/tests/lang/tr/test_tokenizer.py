# coding: utf-8
from __future__ import unicode_literals

import pytest


ABBREV_TESTS = [
        ("Dr. Murat Bey ile görüştüm.", ["Dr.", "Murat", "Bey", "ile", "görüştüm", "."]),
        ("TBMM'de çalışıyormuş.", ["TBMM'de", "çalışıyormuş", "."]),
        ("Hem İst. hem Ank. bu konuda gayet iyi durumda.", ["Hem", "İst.", "hem", "Ank.", "bu", "konuda", "gayet", "iyi", "durumda", "."]),
        ("Hem İst. hem Ank.'da yağış var.", ["Hem", "İst.", "hem", "Ank.'da", "yağış", "var", "."]),
        ("Dr.", ["Dr."]),
        ("Yrd.Doç.", ["Yrd.Doç."]),
        ("Prof.'un", ["Prof.'un"]),
        ("Böl.'nde", ["Böl.'nde"])
]



NUMBER_TESTS = [
        ("Yarışta 6. oldum.", ["Yarışta", "6.", "oldum", "."]),
        ("Yarışta 438547745. oldum.", ["Yarışta", "438547745.", "oldum", "."]),
        ("Kitap IV. Murat hakkında.",["Kitap", "IV.", "Murat", "hakkında", "."]),
        ("Bana söylediği sayı 6.", ["Bana", "söylediği", "sayı", "6", "."]),
        ("Saat 6'da buluşalım.", ["Saat", "6'da", "buluşalım", "."]),
        ("Saat 6dan sonra buluşalım.", ["Saat", "6dan", "sonra", "buluşalım", "."]),
        ("6.dan sonra saymadım.", ["6.dan", "sonra", "saymadım", "."]),
        ("6.'dan sonra saymadım.", ["6.'dan", "sonra", "saymadım", "."]),
        ("Saat 6'ydı.", ["Saat", "6'ydı", "."]),
        ("5'te", ["5'te"]),
        ("6'da", ["6'da"]),
        ("9dan", ["9dan"]),
        ("19'da", ["19'da"]),
        ("VI'da", ["VI'da"]),
        ("5.", ["5", "."]),
        ("72.", ["72", "."]),
        ("VI.", ["VI", "."]),
        ("6.'dan", ["6.'dan"]),
        ("19.'dan", ["19.'dan"]),
        ("6.dan", ["6.dan"]),
        ("16.dan", ["16.dan"]),
        ("VI.'dan", ["VI.'dan"]),
        ("VI.dan", ["VI.dan"])
]


PUNCT_TESTS = [
]

GENERAL_TESTS = [

]

TESTS = (ABBREV_TESTS + NUMBER_TESTS + PUNCT_TESTS + GENERAL_TESTS)

@pytest.mark.parametrize("text", ["Ahmet'te", "Istanbul'da"])
def test_tr_tokenizer_handles_apostrophe(tr_tokenizer, text):
    tokens = tr_tokenizer(text)
    assert len(tokens) == 1



def test_tr_tokenizer_handles_exc_in_text(tr_tokenizer):
    text = "Dr. Murat Bey ile görüştüm."
    tokens = tr_tokenizer(text)
    assert len(tokens) == 6
    assert tokens[0].text == "Dr."
    assert tokens[0].lemma_ == "doktor"



@pytest.mark.parametrize("text,expected_tokens", TESTS)
def test_tr_tokenizer_handles_allcases(tr_tokenizer, text, expected_tokens):
    tokens = tr_tokenizer(text)
    token_list = [token.text for token in tokens if not token.is_space]
    assert expected_tokens == token_list


