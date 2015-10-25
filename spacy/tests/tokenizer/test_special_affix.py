"""Test entries in the tokenization special-case interacting with prefix
and suffix punctuation."""
from __future__ import unicode_literals
import pytest


def test_no_special(en_tokenizer):
    assert len(en_tokenizer("(can)")) == 3


def test_no_punct(en_tokenizer):
    assert len(en_tokenizer("can't")) == 2


def test_prefix(en_tokenizer):
    assert len(en_tokenizer("(can't")) == 3


def test_suffix(en_tokenizer):
    assert len(en_tokenizer("can't)")) == 3


def test_wrap(en_tokenizer):
    assert len(en_tokenizer("(can't)")) == 4


def test_uneven_wrap(en_tokenizer):
    assert len(en_tokenizer("(can't?)")) == 5


def test_prefix_interact(en_tokenizer):
    assert len(en_tokenizer("U.S.")) == 1
    assert len(en_tokenizer("us.")) == 2
    assert len(en_tokenizer("(U.S.")) == 2


def test_suffix_interact(en_tokenizer):
    assert len(en_tokenizer("U.S.)")) == 2


def test_even_wrap_interact(en_tokenizer):
    assert len(en_tokenizer("(U.S.)")) == 3


def test_uneven_wrap_interact(en_tokenizer):
    assert len(en_tokenizer("(U.S.?)")) == 4
