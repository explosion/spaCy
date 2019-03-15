# coding: utf-8
from __future__ import unicode_literals

import pytest


@pytest.mark.parametrize(
    "text,num_tokens",
    [
        (
            "De aftredende minister-president benadrukte al dat zijn partij inhoudelijk weinig gemeen heeft met de groenen.",
            16,
        ),
        ("Hij is sociaal-cultureel werker.", 5),
        ("Er staan een aantal dure auto's in de garage.", 10),
    ],
)
def test_tokenizer_doesnt_split_hyphens(nl_tokenizer, text, num_tokens):
    tokens = nl_tokenizer(text)
    assert len(tokens) == num_tokens
