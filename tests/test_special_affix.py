"""Test entries in the tokenization special-case interacting with prefix
and suffix punctuation."""
from __future__ import unicode_literals
import pytest

from spacy.en import English

@pytest.fixture
def EN():
    return English().tokenizer


def test_no_special(EN):
    assert len(EN("(can)")) == 3

def test_no_punct(EN):
    assert len(EN("can't")) == 2

def test_prefix(EN):
    assert len(EN("(can't")) == 3


def test_suffix(EN):
    assert len(EN("can't)")) == 3


def test_wrap(EN):
    assert len(EN("(can't)")) == 4


def test_uneven_wrap(EN):
    assert len(EN("(can't?)")) == 5


def test_prefix_interact(EN):
    assert len(EN("U.S.")) == 1
    assert len(EN("us.")) == 2
    assert len(EN("(U.S.")) == 2


def test_suffix_interact(EN):
    assert len(EN("U.S.)")) == 2


def test_even_wrap_interact(EN):
    assert len(EN("(U.S.)")) == 3


def test_uneven_wrap_interact(EN):
    assert len(EN("(U.S.?)")) == 4
