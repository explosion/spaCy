# coding: utf-8
from __future__ import unicode_literals

import pytest
import numpy
from spacy.attrs import IS_ALPHA, IS_DIGIT
from spacy.util import OOV_RANK


@pytest.mark.parametrize("text1,prob1,text2,prob2", [("NOUN", -1, "opera", -2)])
def test_vocab_lexeme_lt(en_vocab, text1, text2, prob1, prob2):
    """More frequent is l.t. less frequent"""
    lex1 = en_vocab[text1]
    lex1.prob = prob1
    lex2 = en_vocab[text2]
    lex2.prob = prob2

    assert lex1 < lex2
    assert lex2 > lex1


@pytest.mark.parametrize("text1,text2", [("phantom", "opera")])
def test_vocab_lexeme_hash(en_vocab, text1, text2):
    """Test that lexemes are hashable."""
    lex1 = en_vocab[text1]
    lex2 = en_vocab[text2]
    lexes = {lex1: lex1, lex2: lex2}
    assert lexes[lex1].orth_ == text1
    assert lexes[lex2].orth_ == text2


def test_vocab_lexeme_is_alpha(en_vocab):
    assert en_vocab["the"].flags & (1 << IS_ALPHA)
    assert not en_vocab["1999"].flags & (1 << IS_ALPHA)
    assert not en_vocab["hello1"].flags & (1 << IS_ALPHA)


def test_vocab_lexeme_is_digit(en_vocab):
    assert not en_vocab["the"].flags & (1 << IS_DIGIT)
    assert en_vocab["1999"].flags & (1 << IS_DIGIT)
    assert not en_vocab["hello1"].flags & (1 << IS_DIGIT)


def test_vocab_lexeme_add_flag_auto_id(en_vocab):
    is_len4 = en_vocab.add_flag(lambda string: len(string) == 4)
    assert en_vocab["1999"].check_flag(is_len4) is True
    assert en_vocab["1999"].check_flag(IS_DIGIT) is True
    assert en_vocab["199"].check_flag(is_len4) is False
    assert en_vocab["199"].check_flag(IS_DIGIT) is True
    assert en_vocab["the"].check_flag(is_len4) is False
    assert en_vocab["dogs"].check_flag(is_len4) is True


def test_vocab_lexeme_add_flag_provided_id(en_vocab):
    is_len4 = en_vocab.add_flag(lambda string: len(string) == 4, flag_id=IS_DIGIT)
    assert en_vocab["1999"].check_flag(is_len4) is True
    assert en_vocab["199"].check_flag(is_len4) is False
    assert en_vocab["199"].check_flag(IS_DIGIT) is False
    assert en_vocab["the"].check_flag(is_len4) is False
    assert en_vocab["dogs"].check_flag(is_len4) is True


def test_vocab_lexeme_oov_rank(en_vocab):
    """Test that default rank is OOV_RANK."""
    lex = en_vocab["word"]
    assert OOV_RANK == numpy.iinfo(numpy.uint64).max
    assert lex.rank == OOV_RANK
