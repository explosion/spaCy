# encoding: utf8
from __future__ import unicode_literals

import pytest


@pytest.mark.parametrize('text,expected_tokens',
    [('פייתון היא שפת תכנות דינמית', ['פייתון', 'היא', 'שפת', 'תכנות', 'דינמית'])])
def test_tokenizer_handles_abbreviation(he_tokenizer, text, expected_tokens):
    tokens = he_tokenizer(text)
    token_list = [token.text for token in tokens if not token.is_space]
    assert expected_tokens == token_list


@pytest.mark.parametrize('text,expected_tokens', [
    ('עקבת אחריו בכל רחבי המדינה.', ['עקבת', 'אחריו', 'בכל', 'רחבי', 'המדינה', '.']),
    ('עקבת אחריו בכל רחבי המדינה?', ['עקבת', 'אחריו', 'בכל', 'רחבי', 'המדינה', '?']),
    ('עקבת אחריו בכל רחבי המדינה!', ['עקבת', 'אחריו', 'בכל', 'רחבי', 'המדינה', '!']),
    ('עקבת אחריו בכל רחבי המדינה..', ['עקבת', 'אחריו', 'בכל', 'רחבי', 'המדינה', '..']),
    ('עקבת אחריו בכל רחבי המדינה...', ['עקבת', 'אחריו', 'בכל', 'רחבי', 'המדינה', '...'])])
def test_tokenizer_handles_punct(he_tokenizer, text, expected_tokens):
    tokens = he_tokenizer(text)
    assert expected_tokens == [token.text for token in tokens]
