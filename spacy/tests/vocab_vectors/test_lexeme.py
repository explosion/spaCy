import numpy
import pytest
from spacy.attrs import IS_ALPHA, IS_DIGIT
from spacy.lookups import Lookups
from spacy.tokens import Doc
from spacy.util import OOV_RANK, DEFAULT_OOV_PROB
from spacy.vocab import Vocab


@pytest.mark.issue(361)
@pytest.mark.parametrize("text1,text2", [("cat", "dog")])
def test_issue361(en_vocab, text1, text2):
    """Test Issue #361: Equality of lexemes"""
    assert en_vocab[text1] == en_vocab[text1]
    assert en_vocab[text1] != en_vocab[text2]


@pytest.mark.issue(600)
def test_issue600():
    vocab = Vocab()
    doc = Doc(vocab, words=["hello"])
    doc[0].tag_ = "NN"


@pytest.mark.parametrize("word1,prob1,word2,prob2", [("NOUN", -1, "opera", -2)])
def test_vocab_lexeme_prob(word1, word2, prob1, prob2):
    """lexeme_prob table is only added if custom probs are set"""
    vocab = Vocab()
    # blank vocab does not include this table
    assert "lexeme_prob" not in vocab.lookups.tables
    # accessing a prob does not add a table
    assert vocab["OTHER"].prob == DEFAULT_OOV_PROB
    assert "lexeme_prob" not in vocab.lookups.tables
    # table is added when a prob is set
    vocab[word1].prob = -1
    assert "lexeme_prob" in vocab.lookups.tables
    assert word2 not in vocab.lookups.get_table("lexeme_prob")
    vocab[word2].prob = prob2
    assert vocab[word1].prob > vocab[word2].prob


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
    en_vocab.add_flag(lambda string: string.isdigit(), flag_id=IS_DIGIT)


def test_vocab_lexeme_oov_rank(en_vocab):
    """Test that default rank is OOV_RANK."""
    lex = en_vocab["word"]
    assert OOV_RANK == numpy.iinfo(numpy.uint64).max
    assert lex.rank == OOV_RANK
