# coding: utf8
from __future__ import unicode_literals
from ..util import add_vecs_to_vocab, get_doc
import pytest

@pytest.fixture
def vectors():
    return [("a", [1, 2, 3]), ("letter", [4, 5, 6])]

@pytest.fixture
def vocab(en_vocab, vectors):
    add_vecs_to_vocab(en_vocab, vectors)
    return en_vocab

def test_issue2219(vocab, vectors):
    [(word1, vec1), (word2, vec2)] = vectors
    doc = get_doc(vocab, words=[word1, word2])
    assert doc[0].similarity(doc[1]) == doc[1].similarity(doc[0])
