# coding: utf-8
from __future__ import unicode_literals

from ...lang.da.lex_attrs import like_num as da_like_num
# from ...lang.en.lex_attrs import like_num as en_like_num
# from ...lang.fr.lex_attrs import like_num as fr_like_num
# from ...lang.id.lex_attrs import like_num as id_like_num
# from ...lang.nl.lex_attrs import like_num as nl_like_num
# from ...lang.pt.lex_attrs import like_num as pt_like_num
# from ...lang.ru.lex_attrs import like_num as ru_like_num

import pytest


@pytest.mark.parametrize('num_words', ['elleve', 'ELLEVE'])
@pytest.mark.parametrize('ordinal_words', ['første', 'FØRSTE'])
def test_da_lex_attrs(num_words, ordinal_words):
    assert da_like_num(num_words) == True
    assert da_like_num(ordinal_words) == True


# @pytest.mark.parametrize('num_words', ['eleven', 'ELEVEN'])
# def test_en_lex_attrs(num_words):
#     assert en_like_num(num_words) == True
#
#
# @pytest.mark.parametrize('num_words', ['onze', 'ONZE'])
# @pytest.mark.parametrize('ordinal_words', ['onzième', 'ONZIÈME'])
# def test_fr_lex_attrs(num_words, ordinal_words):
#     assert fr_like_num(num_words) == True
#     assert fr_like_num(ordinal_words) == True
#
#
# @pytest.mark.parametrize('num_words', ['sebelas', 'SEBELAS'])
# def test_id_lex_attrs(num_words):
#     assert id_like_num(num_words) == True
#
#
# @pytest.mark.parametrize('num_words', ['elf', 'ELF'])
# @pytest.mark.parametrize('ordinal_words', ['elfde', 'ELFDE'])
# def test_nl_lex_attrs(num_words, ordinal_words):
#     assert nl_like_num(num_words) == True
#     assert nl_like_num(ordinal_words) == True
#
#
# @pytest.mark.parametrize('num_words', ['onze', 'ONZE'])
# @pytest.mark.parametrize('ordinal_words', ['quadragésimo', 'QUADRAGÉSIMO'])
# def test_pt_lex_attrs(num_words, ordinal_words):
#     assert pt_like_num(num_words) == True
#     assert pt_like_num(ordinal_words) == True
#
#
# @pytest.mark.parametrize('num_words', ['одиннадцать', 'ОДИННАДЦАТЬ'])
# def test_ru_lex_attrs(num_words):
#     assert ru_like_num(num_words) == True
