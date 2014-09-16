"""Test entries in the tokenization special-case interacting with prefix
and suffix punctuation."""
from __future__ import unicode_literals
import pytest

from spacy.en import EN

def test_no_special():
    assert len(EN.tokenize("(can)")) == 3

def test_no_punct():
    assert len(EN.tokenize("can't")) == 2

def test_prefix():
    assert len(EN.tokenize("(can't")) == 3


def test_suffix():
    assert len(EN.tokenize("can't)")) == 3


def test_wrap():
    assert len(EN.tokenize("(can't)")) == 4


def test_uneven_wrap():
    assert len(EN.tokenize("(can't?)")) == 5


def test_prefix_interact():
    assert len(EN.tokenize("U.S.")) == 1
    assert len(EN.tokenize("us.")) == 2
    assert len(EN.tokenize("(U.S.")) == 2


def test_suffix_interact():
    assert len(EN.tokenize("U.S.)")) == 2


def test_even_wrap_interact():
    assert len(EN.tokenize("(U.S.)")) == 3


def test_uneven_wrap_interact():
    assert len(EN.tokenize("(U.S.?)")) == 4
