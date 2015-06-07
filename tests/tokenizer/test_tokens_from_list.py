from __future__ import unicode_literals
import pytest

from spacy.en import English


@pytest.fixture
def EN():
    return English()


def test1(EN):
    words = ['JAPAN', 'GET', 'LUCKY']
    tokens = EN.tokenizer.tokens_from_list(words)
    assert len(tokens) == 3
    assert tokens[0].orth_ == 'JAPAN'
