# encoding: utf8
from __future__ import unicode_literals

import pytest

SV_TOKEN_EXCEPTION_TESTS = [
    ('Smörsåsen används bl.a. till fisk', ['Smörsåsen', 'används', 'bl.a.', 'till', 'fisk']),
    ('Jag kommer först kl. 13 p.g.a. diverse förseningar', ['Jag', 'kommer', 'först', 'kl.', '13', 'p.g.a.', 'diverse', 'förseningar'])
]

@pytest.mark.parametrize('text,expected_tokens', SV_TOKEN_EXCEPTION_TESTS)
def test_issue805(sv_tokenizer, text, expected_tokens):
    tokens = sv_tokenizer(text)
    token_list = [token.text for token in tokens if not token.is_space]
    assert expected_tokens == token_list
