import pytest
import numpy
from spacy.tokens import Doc

from ..util import get_cosine, add_vecs_to_vocab


@pytest.fixture
def vectors():
    return [("apple", [1, 2, 3]), ("orange", [-1, -2, -3])]


@pytest.fixture()
def vocab(en_vocab, vectors):
    add_vecs_to_vocab(en_vocab, vectors)
    return en_vocab


@pytest.mark.issue(2219)
def test_issue2219(en_vocab):
    """Test if indexing issue still occurs during Token-Token similarity"""
    vectors = [("a", [1, 2, 3]), ("letter", [4, 5, 6])]
    add_vecs_to_vocab(en_vocab, vectors)
    [(word1, vec1), (word2, vec2)] = vectors
    doc = Doc(en_vocab, words=[word1, word2])
    assert doc[0].similarity(doc[1]) == doc[1].similarity(doc[0])


def test_vectors_similarity_LL(vocab, vectors):
    [(word1, vec1), (word2, vec2)] = vectors
    lex1 = vocab[word1]
    lex2 = vocab[word2]
    assert lex1.has_vector
    assert lex2.has_vector
    assert lex1.vector_norm != 0
    assert lex2.vector_norm != 0
    assert lex1.vector[0] != lex2.vector[0] and lex1.vector[1] != lex2.vector[1]
    assert numpy.isclose(lex1.similarity(lex2), get_cosine(vec1, vec2))
    assert numpy.isclose(lex2.similarity(lex2), lex1.similarity(lex1))


def test_vectors_similarity_TT(vocab, vectors):
    [(word1, vec1), (word2, vec2)] = vectors
    doc = Doc(vocab, words=[word1, word2])
    assert doc[0].has_vector
    assert doc[1].has_vector
    assert doc[0].vector_norm != 0
    assert doc[1].vector_norm != 0
    assert doc[0].vector[0] != doc[1].vector[0] and doc[0].vector[1] != doc[1].vector[1]
    assert numpy.isclose(doc[0].similarity(doc[1]), get_cosine(vec1, vec2))
    assert numpy.isclose(doc[1].similarity(doc[0]), doc[0].similarity(doc[1]))


def test_vectors_similarity_TD(vocab, vectors):
    [(word1, vec1), (word2, vec2)] = vectors
    doc = Doc(vocab, words=[word1, word2])
    with pytest.warns(UserWarning):
        assert doc.similarity(doc[0]) == doc[0].similarity(doc)


def test_vectors_similarity_DS(vocab, vectors):
    [(word1, vec1), (word2, vec2)] = vectors
    doc = Doc(vocab, words=[word1, word2])
    assert doc.similarity(doc[:2]) == doc[:2].similarity(doc)


def test_vectors_similarity_TS(vocab, vectors):
    [(word1, vec1), (word2, vec2)] = vectors
    doc = Doc(vocab, words=[word1, word2])
    with pytest.warns(UserWarning):
        assert doc[:2].similarity(doc[0]) == doc[0].similarity(doc[:2])
