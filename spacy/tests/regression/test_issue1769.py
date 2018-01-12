# coding: utf-8
from __future__ import unicode_literals
from ...util import get_lang_class
from ...attrs import LIKE_NUM

import pytest


@pytest.mark.parametrize('word', ['eleven'])
def test_en_lex_attrs(word):
    lang = get_lang_class('en')
    like_num = lang.Defaults.lex_attr_getters[LIKE_NUM]
    assert like_num(word) == like_num(word.upper())


@pytest.mark.slow
@pytest.mark.parametrize('word', ['elleve', 'første'])
def test_da_lex_attrs(word):
    lang = get_lang_class('da')
    like_num = lang.Defaults.lex_attr_getters[LIKE_NUM]
    assert like_num(word) == like_num(word.upper())


@pytest.mark.slow
@pytest.mark.parametrize('word', ['onze', 'onzième'])
def test_fr_lex_attrs(word):
    lang = get_lang_class('fr')
    like_num = lang.Defaults.lex_attr_getters[LIKE_NUM]
    assert like_num(word) == like_num(word.upper())


@pytest.mark.slow
@pytest.mark.parametrize('word', ['sebelas'])
def test_id_lex_attrs(word):
    lang = get_lang_class('id')
    like_num = lang.Defaults.lex_attr_getters[LIKE_NUM]
    assert like_num(word) == like_num(word.upper())


@pytest.mark.slow
@pytest.mark.parametrize('word', ['elf', 'elfde'])
def test_nl_lex_attrs(word):
    lang = get_lang_class('nl')
    like_num = lang.Defaults.lex_attr_getters[LIKE_NUM]
    assert like_num(word) == like_num(word.upper())


@pytest.mark.slow
@pytest.mark.parametrize('word', ['onze', 'quadragésimo'])
def test_pt_lex_attrs(word):
    lang = get_lang_class('pt')
    like_num = lang.Defaults.lex_attr_getters[LIKE_NUM]
    assert like_num(word) == like_num(word.upper())


@pytest.mark.slow
@pytest.mark.parametrize('word', ['одиннадцать'])
def test_ru_lex_attrs(word):
    lang = get_lang_class('ru')
    like_num = lang.Defaults.lex_attr_getters[LIKE_NUM]
    assert like_num(word) == like_num(word.upper())
