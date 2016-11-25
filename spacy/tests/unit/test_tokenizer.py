from __future__ import unicode_literals
import pytest
import re

from ...vocab import Vocab
from ...tokenizer import Tokenizer


@pytest.fixture
def vocab():
    return Vocab(tag_map={'NN': {'pos': 'NOUN'}})

@pytest.fixture
def rules():
    return {}

@pytest.fixture
def prefix_search():
    return None

@pytest.fixture
def suffix_search():
    return None

@pytest.fixture
def infix_finditer():
    return None


@pytest.fixture
def tokenizer(vocab, rules, prefix_search, suffix_search, infix_finditer):
    return Tokenizer(vocab, rules, prefix_search, suffix_search, infix_finditer)


def test_add_special_case(tokenizer):
    tokenizer.add_special_case('dog', [{'orth': 'd'}, {'orth': 'og'}])
    doc = tokenizer('dog')
    assert doc[0].text == 'd'
    assert doc[1].text == 'og'


def test_special_case_tag(tokenizer):
    tokenizer.add_special_case('dog', [{'orth': 'd', 'tag': 'NN'}, {'orth': 'og'}])
    doc = tokenizer('dog')
    assert doc[0].text == 'd'
    assert doc[0].tag_ == 'NN'
    assert doc[0].pos_ == 'NOUN'
    assert doc[1].text == 'og'
