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


@pytest.fixture
def words():
    return {
        "da": {
            "num_words": ('elleve', 'ELLEVE')
        },
        "en": {
            "num_words": ('eleven', 'ELEVEN')
        },
        "fr": {
            "num_words": ('onze', 'ONZE')
        },
        "id": {
            "num_words": ('sebelas', 'SEBELAS')
        },
        "nl": {
            "num_words": ('elf', 'ELF')
        },
        "pt": {
            "num_words": ('onze', 'ONZE')
        },
        "ru": {
            "num_words": ('одиннадцать', 'ОДИННАДЦАТЬ')
        }
    }


def like_num(words, fn):
    ok = True
    for word in words:
        if fn(word) is not True:
            ok = False
            break
    return ok


def test_da_lex_attrs(words):
    assert like_num(words["da"]["num_words"], da_like_num) == True


def test_en_lex_attrs(words):
    assert like_num(words["en"]["num_words"], en_like_num) == True


def test_fr_lex_attrs(words):
    assert like_num(words["fr"]["num_words"], fr_like_num) == True


def test_id_lex_attrs(words):
    assert like_num(words["id"]["num_words"], id_like_num) == True


def test_nl_lex_attrs(words):
    assert like_num(words["nl"]["num_words"], nl_like_num) == True


def test_pt_lex_attrs(words):
    assert like_num(words["pt"]["num_words"], pt_like_num) == True


def test_ru_lex_attrs(words):
    assert like_num(words["ru"]["num_words"], ru_like_num) == True
