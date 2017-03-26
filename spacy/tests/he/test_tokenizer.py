# encoding: utf8
from __future__ import unicode_literals

import pytest

ABBREVIATION_TESTS = [
    ('פייתון היא שפת תכנות דינמית', ['פייתון', 'היא', 'שפת', 'תכנות', 'דינמית'])
]

TESTCASES = ABBREVIATION_TESTS


@pytest.mark.parametrize('text,expected_tokens', TESTCASES)
def test_tokenizer_handles_testcases(he_tokenizer, text, expected_tokens):
    tokens = he_tokenizer(text)
    token_list = [token.text for token in tokens if not token.is_space]
    assert expected_tokens == token_list