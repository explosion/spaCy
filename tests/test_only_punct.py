from __future__ import unicode_literals
import pytest

from spacy.en import EN

def test_only_pre1():
    assert len(EN.tokenize("(")) == 1


def test_only_pre2():
    assert len(EN.tokenize("((")) == 2

def test_only_suf2():
    assert len(EN.tokenize("''")) == 2
