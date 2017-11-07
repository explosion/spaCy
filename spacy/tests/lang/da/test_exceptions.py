# coding: utf-8
from __future__ import unicode_literals

import pytest

@pytest.mark.parametrize('text', ["ca.", "m.a.o.", "Jan.", "Dec."])
def test_da_tokenizer_handles_abbr(da_tokenizer, text):
    tokens = da_tokenizer(text)
    assert len(tokens) == 1

def test_da_tokenizer_handles_exc_in_text(da_tokenizer):
    text = "Det er bl.a. ikke meningen"
    tokens = da_tokenizer(text)
    assert len(tokens) == 5
    assert tokens[2].text == "bl.a."
