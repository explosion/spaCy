# coding: utf-8
from __future__ import unicode_literals
from ...lang.lex_attrs import is_stop
from ...lang.en.stop_words import STOP_WORDS

import pytest


@pytest.mark.parametrize('word', ['the'])
def test_lex_attrs_stop_words_case_sensitivity(word):
    assert is_stop(word, STOP_WORDS) == is_stop(word.upper(), STOP_WORDS)
