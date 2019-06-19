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
    "text,norm", [("akvarium", "akvarie"), ("bedstemoder", "bedstemor")]
)
def test_da_tokenizer_norm_exceptions(da_tokenizer, text, norm):
    tokens = da_tokenizer(text)
    assert tokens[0].norm_ == norm
