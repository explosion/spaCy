# coding: utf-8
from __future__ import unicode_literals

from ...tokenizer import Tokenizer
from ..util import get_doc, add_vecs_to_vocab

import pytest


@pytest.fixture
def vectors():
    return [("apple", [0.0, 1.0, 2.0]), ("orange", [3.0, -2.0, 4.0])]


@pytest.fixture()
def vocab(en_vocab, vectors):
    return add_vecs_to_vocab(en_vocab, vectors)


@pytest.fixture()
def tokenizer_v(vocab):
    return Tokenizer(vocab, {}, None, None, None)


@pytest.mark.parametrize('text', ["apple and orange"])
def test_vectors_token_vector(tokenizer_v, vectors, text):
    doc = tokenizer_v(text)
    assert vectors[0] == (doc[0].text, list(doc[0].vector))
    assert vectors[1] == (doc[2].text, list(doc[2].vector))


@pytest.mark.parametrize('text', ["apple", "orange"])
def test_vectors_lexeme_vector(vocab, text):
    lex = vocab[text]
    assert list(lex.vector)
    assert lex.vector_norm


@pytest.mark.parametrize('text', [["apple", "and", "orange"]])
def test_vectors_doc_vector(vocab, text):
    doc = get_doc(vocab, text)
    assert list(doc.vector)
    assert doc.vector_norm


@pytest.mark.parametrize('text', [["apple", "and", "orange"]])
def test_vectors_span_vector(vocab, text):
    span = get_doc(vocab, text)[0:2]
    assert list(span.vector)
    assert span.vector_norm


@pytest.mark.parametrize('text', ["apple orange"])
def test_vectors_token_token_similarity(tokenizer_v, text):
    doc = tokenizer_v(text)
    assert doc[0].similarity(doc[1]) == doc[1].similarity(doc[0])
    assert 0.0 < doc[0].similarity(doc[1]) < 1.0


@pytest.mark.parametrize('text1,text2', [("apple", "orange")])
def test_vectors_token_lexeme_similarity(tokenizer_v, vocab, text1, text2):
    token = tokenizer_v(text1)
    lex = vocab[text2]
    assert token.similarity(lex) == lex.similarity(token)
    assert 0.0 < token.similarity(lex) < 1.0


@pytest.mark.parametrize('text', [["apple", "orange", "juice"]])
def test_vectors_token_span_similarity(vocab, text):
    doc = get_doc(vocab, text)
    assert doc[0].similarity(doc[1:3]) == doc[1:3].similarity(doc[0])
    assert 0.0 < doc[0].similarity(doc[1:3]) < 1.0


@pytest.mark.parametrize('text', [["apple", "orange", "juice"]])
def test_vectors_token_doc_similarity(vocab, text):
    doc = get_doc(vocab, text)
    assert doc[0].similarity(doc) == doc.similarity(doc[0])
    assert 0.0 < doc[0].similarity(doc) < 1.0


@pytest.mark.parametrize('text', [["apple", "orange", "juice"]])
def test_vectors_lexeme_span_similarity(vocab, text):
    doc = get_doc(vocab, text)
    lex = vocab[text[0]]
    assert lex.similarity(doc[1:3]) == doc[1:3].similarity(lex)
    assert 0.0 < doc.similarity(doc[1:3]) < 1.0


@pytest.mark.parametrize('text1,text2', [("apple", "orange")])
def test_vectors_lexeme_lexeme_similarity(vocab, text1, text2):
    lex1 = vocab[text1]
    lex2 = vocab[text2]
    assert lex1.similarity(lex2) == lex2.similarity(lex1)
    assert 0.0 < lex1.similarity(lex2) < 1.0


@pytest.mark.parametrize('text', [["apple", "orange", "juice"]])
def test_vectors_lexeme_doc_similarity(vocab, text):
    doc = get_doc(vocab, text)
    lex = vocab[text[0]]
    assert lex.similarity(doc) == doc.similarity(lex)
    assert 0.0 < lex.similarity(doc) < 1.0


@pytest.mark.parametrize('text', [["apple", "orange", "juice"]])
def test_vectors_span_span_similarity(vocab, text):
    doc = get_doc(vocab, text)
    assert doc[0:2].similarity(doc[1:3]) == doc[1:3].similarity(doc[0:2])
    assert 0.0 < doc[0:2].similarity(doc[1:3]) < 1.0


@pytest.mark.parametrize('text', [["apple", "orange", "juice"]])
def test_vectors_span_doc_similarity(vocab, text):
    doc = get_doc(vocab, text)
    assert doc[0:2].similarity(doc) == doc.similarity(doc[0:2])
    assert 0.0 < doc[0:2].similarity(doc) < 1.0


@pytest.mark.parametrize('text1,text2', [
    (["apple", "and", "apple", "pie"], ["orange", "juice"])])
def test_vectors_doc_doc_similarity(vocab, text1, text2):
    doc1 = get_doc(vocab, text1)
    doc2 = get_doc(vocab, text2)
    assert doc1.similarity(doc2) == doc2.similarity(doc1)
    assert 0.0 < doc1.similarity(doc2) < 1.0
