# coding: utf-8
from __future__ import unicode_literals

from ...lang.da.lex_attrs import like_num as da_like_num
from ...lang.en.lex_attrs import like_num as en_like_num
from ...lang.fr.lex_attrs import like_num as fr_like_num
from ...lang.id.lex_attrs import like_num as id_like_num
from ...lang.nl.lex_attrs import like_num as nl_like_num
from ...lang.pt.lex_attrs import like_num as pt_like_num
from ...lang.ru.lex_attrs import like_num as ru_like_num

import pytest


@pytest.mark.parametrize('word', ['elleve', 'første'])
def test_da_lex_attrs(word):
    assert da_like_num(word) == da_like_num(word.upper())


@pytest.mark.parametrize('word', ['eleven'])
def test_en_lex_attrs(word):
    assert en_like_num(word) == en_like_num(word.upper())


@pytest.mark.parametrize('word', ['onze', 'onzième'])
def test_fr_lex_attrs(word):
    assert fr_like_num(word) == fr_like_num(word.upper())


@pytest.mark.parametrize('word', ['sebelas'])
def test_id_lex_attrs(word):
    assert id_like_num(word) == id_like_num(word.upper())


@pytest.mark.parametrize('word', ['elf', 'elfde'])
def test_nl_lex_attrs(word):
    assert nl_like_num(word) == nl_like_num(word.upper())


@pytest.mark.parametrize('word', ['onze', 'quadragésimo'])
def test_pt_lex_attrs(word):
    assert pt_like_num(word) == pt_like_num(word.upper())


@pytest.mark.parametrize('word', ['одиннадцать'])
def test_ru_lex_attrs(word):
    assert ru_like_num(word) == ru_like_num(word.upper())
