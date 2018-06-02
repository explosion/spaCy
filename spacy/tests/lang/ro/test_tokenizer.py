# coding: utf8
from __future__ import unicode_literals

import pytest

DEFAULT_TESTS = [
    ('Adresa este str. Principală nr. 5.', ['Adresa', 'este', 'str.', 'Principală', 'nr.', '5', '.']),
    ('Teste, etc.', ['Teste', ',', 'etc.']),
    ('Lista, ș.a.m.d.', ['Lista', ',', 'ș.a.m.d.']),
    ('Și d.p.d.v. al...', ['Și', 'd.p.d.v.', 'al', '...'])
]

NUMBER_TESTS = [
    ('Clasa a 4-a.', ['Clasa', 'a', '4-a', '.']),
    ('Al 12-lea ceas.', ['Al', '12-lea', 'ceas', '.'])
]

TESTCASES = DEFAULT_TESTS + NUMBER_TESTS


@pytest.mark.parametrize('text,expected_tokens', TESTCASES)
def test_tokenizer_handles_testcases(ro_tokenizer, text, expected_tokens):
    tokens = ro_tokenizer(text)
    token_list = [token.text for token in tokens if not token.is_space]
    assert expected_tokens == token_list
