# coding: utf8
from __future__ import unicode_literals

import pytest
from spacy.util import get_lang_class


NB_TOKEN_EXCEPTION_TESTS = [
    (
        "Smørsausen brukes bl.a. til fisk",
        ["Smørsausen", "brukes", "bl.a.", "til", "fisk"],
    ),
    (
        "Jeg kommer først kl. 13 pga. diverse forsinkelser",
        ["Jeg", "kommer", "først", "kl.", "13", "pga.", "diverse", "forsinkelser"],
    ),
]


@pytest.mark.parametrize("text,expected_tokens", NB_TOKEN_EXCEPTION_TESTS)
def test_no_tokenizer_handles_exception_cases(no_tokenizer, text, expected_tokens):
    tokens = no_tokenizer(text)
    token_list = [token.text for token in tokens if not token.is_space]
    assert expected_tokens == token_list


def test_no_nb_warning():
    with pytest.warns(UserWarning):
        get_lang_class("nb")
