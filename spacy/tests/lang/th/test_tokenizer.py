# coding: utf8
from __future__ import unicode_literals

import pytest

TOKENIZER_TESTS = [
        ("คุณรักผมไหม", ['คุณ', 'รัก', 'ผม', 'ไหม'])
]

@pytest.mark.parametrize('text,expected_tokens', TOKENIZER_TESTS)
def test_thai_tokenizer(th_tokenizer, text, expected_tokens):
	tokens = [token.text for token in th_tokenizer(text)]
	assert tokens == expected_tokens
