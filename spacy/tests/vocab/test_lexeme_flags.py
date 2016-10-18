from __future__ import unicode_literals

import pytest

from spacy.attrs import *


def test_is_alpha(en_vocab):
    the = en_vocab['the']
    assert the.flags & (1 << IS_ALPHA)
    year = en_vocab['1999']
    assert not year.flags & (1 << IS_ALPHA)
    mixed = en_vocab['hello1']
    assert not mixed.flags & (1 << IS_ALPHA)


def test_is_digit(en_vocab):
    the = en_vocab['the']
    assert not the.flags & (1 << IS_DIGIT)
    year = en_vocab['1999']
    assert year.flags & (1 << IS_DIGIT)
    mixed = en_vocab['hello1']
    assert not mixed.flags & (1 << IS_DIGIT)


def test_add_flag_auto_id(en_vocab):
    is_len4 = en_vocab.add_flag(lambda string: len(string) == 4)
    assert en_vocab['1999'].check_flag(is_len4) == True
    assert en_vocab['1999'].check_flag(IS_DIGIT) == True
    assert en_vocab['199'].check_flag(is_len4) == False
    assert en_vocab['199'].check_flag(IS_DIGIT) == True
    assert en_vocab['the'].check_flag(is_len4) == False
    assert en_vocab['dogs'].check_flag(is_len4) == True


def test_add_flag_provided_id(en_vocab):
    is_len4 = en_vocab.add_flag(lambda string: len(string) == 4, flag_id=IS_DIGIT)
    assert en_vocab['1999'].check_flag(is_len4) == True
    assert en_vocab['199'].check_flag(is_len4) == False
    assert en_vocab['199'].check_flag(IS_DIGIT) == False
    assert en_vocab['the'].check_flag(is_len4) == False
    assert en_vocab['dogs'].check_flag(is_len4) == True
