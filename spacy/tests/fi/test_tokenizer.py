# encoding: utf8
from __future__ import unicode_literals

import pytest

ABBREVIATION_TESTS = [
    ('Hyvää uutta vuotta t. siht. Niemelä!', ['Hyvää', 'uutta', 'vuotta', 't.', 'siht.', 'Niemelä', '!']),
    ('Paino on n. 2.2 kg', ['Paino', 'on', 'n.', '2.2', 'kg'])
]

TESTCASES = ABBREVIATION_TESTS


@pytest.mark.parametrize('text,expected_tokens', TESTCASES)
def test_tokenizer_handles_testcases(fi_tokenizer, text, expected_tokens):
    tokens = fi_tokenizer(text)
    token_list = [token.text for token in tokens if not token.is_space]
    assert expected_tokens == token_list
