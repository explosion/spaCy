# coding: utf-8
from __future__ import unicode_literals

import pytest


@pytest.mark.parametrize("text", ["ca.", "m.a.o.", "Jan.", "Dec.", "kr.", "jf."])
def test_da_tokenizer_handles_abbr(da_tokenizer, text):
    tokens = da_tokenizer(text)
    assert len(tokens) == 1


@pytest.mark.parametrize("text", ["Jul.", "jul.", "Tor.", "Tors."])
def test_da_tokenizer_handles_ambiguous_abbr(da_tokenizer, text):
    tokens = da_tokenizer(text)
    assert len(tokens) == 2


@pytest.mark.parametrize("text", ["1.", "10.", "31."])
def test_da_tokenizer_handles_dates(da_tokenizer, text):
    tokens = da_tokenizer(text)
    assert len(tokens) == 1


def test_da_tokenizer_handles_exc_in_text(da_tokenizer):
    text = "Det er bl.a. ikke meningen"
    tokens = da_tokenizer(text)
    assert len(tokens) == 5
    assert tokens[2].text == "bl.a."


def test_da_tokenizer_handles_custom_base_exc(da_tokenizer):
    text = "Her er noget du kan kigge i."
    tokens = da_tokenizer(text)
    assert len(tokens) == 8
    assert tokens[6].text == "i"
    assert tokens[7].text == "."


@pytest.mark.parametrize(
    "text,n_tokens",
    [
        ("Godt og/eller skidt", 3),
        ("Kør 4 km/t på vejen", 5),
        ("Det blæser 12 m/s.", 5),
        ("Det blæser 12 m/sek. på havnen", 6),
        ("Windows 8/Windows 10", 5),
        ("Billeten virker til bus/tog/metro", 8),
        ("26/02/2019", 1),
        ("Kristiansen c/o Madsen", 3),
        ("Sprogteknologi a/s", 2),
        ("De boede i A/B Bellevue", 5),
        # note: skipping due to weirdness in UD_Danish-DDT
        # ("Rotorhastigheden er 3400 o/m.", 5),
        ("Jeg købte billet t/r.", 5),
        ("Murerarbejdsmand m/k søges", 3),
        ("Netværket kører over TCP/IP", 4),
    ],
)
def test_da_tokenizer_slash(da_tokenizer, text, n_tokens):
    tokens = da_tokenizer(text)
    assert len(tokens) == n_tokens
