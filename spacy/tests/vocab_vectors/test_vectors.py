# coding: utf-8
from __future__ import unicode_literals

import pytest
import numpy
from numpy.testing import assert_allclose
from spacy._ml import cosine
from spacy.vocab import Vocab
from spacy.vectors import Vectors
from spacy.tokenizer import Tokenizer
from spacy.strings import hash_string
from spacy.tokens import Doc

from ..util import add_vecs_to_vocab


@pytest.fixture
def strings():
    return ["apple", "orange"]


@pytest.fixture
def vectors():
    return [
        ("apple", [1, 2, 3]),
        ("orange", [-1, -2, -3]),
        ("and", [-1, -1, -1]),
        ("juice", [5, 5, 10]),
        ("pie", [7, 6.3, 8.9]),
    ]


@pytest.fixture
def ngrams_vectors():
    return [
        ("apple", [1, 2, 3]),
        ("app", [-0.1, -0.2, -0.3]),
        ("ppl", [-0.2, -0.3, -0.4]),
        ("pl", [0.7, 0.8, 0.9]),
    ]


@pytest.fixture()
def ngrams_vocab(en_vocab, ngrams_vectors):
    add_vecs_to_vocab(en_vocab, ngrams_vectors)
    return en_vocab


@pytest.fixture
def data():
    return numpy.asarray([[0.0, 1.0, 2.0], [3.0, -2.0, 4.0]], dtype="f")


@pytest.fixture
def resize_data():
    return numpy.asarray([[0.0, 1.0], [2.0, 3.0]], dtype="f")


@pytest.fixture()
def vocab(en_vocab, vectors):
    add_vecs_to_vocab(en_vocab, vectors)
    return en_vocab


@pytest.fixture()
def tokenizer_v(vocab):
    return Tokenizer(vocab, {}, None, None, None)


def test_init_vectors_with_resize_shape(strings, resize_data):
    v = Vectors(shape=(len(strings), 3))
    v.resize(shape=resize_data.shape)
    assert v.shape == resize_data.shape
    assert v.shape != (len(strings), 3)


def test_init_vectors_with_resize_data(data, resize_data):
    v = Vectors(data=data)
    v.resize(shape=resize_data.shape)
    assert v.shape == resize_data.shape
    assert v.shape != data.shape


def test_get_vector_resize(strings, data, resize_data):
    v = Vectors(data=data)
    v.resize(shape=resize_data.shape)
    strings = [hash_string(s) for s in strings]
    for i, string in enumerate(strings):
        v.add(string, row=i)

    assert list(v[strings[0]]) == list(resize_data[0])
    assert list(v[strings[0]]) != list(resize_data[1])
    assert list(v[strings[1]]) != list(resize_data[0])
    assert list(v[strings[1]]) == list(resize_data[1])


def test_init_vectors_with_data(strings, data):
    v = Vectors(data=data)
    assert v.shape == data.shape


def test_init_vectors_with_shape(strings):
    v = Vectors(shape=(len(strings), 3))
    assert v.shape == (len(strings), 3)


def test_get_vector(strings, data):
    v = Vectors(data=data)
    strings = [hash_string(s) for s in strings]
    for i, string in enumerate(strings):
        v.add(string, row=i)
    assert list(v[strings[0]]) == list(data[0])
    assert list(v[strings[0]]) != list(data[1])
    assert list(v[strings[1]]) != list(data[0])


def test_set_vector(strings, data):
    orig = data.copy()
    v = Vectors(data=data)
    strings = [hash_string(s) for s in strings]
    for i, string in enumerate(strings):
        v.add(string, row=i)
    assert list(v[strings[0]]) == list(orig[0])
    assert list(v[strings[0]]) != list(orig[1])
    v[strings[0]] = data[1]
    assert list(v[strings[0]]) == list(orig[1])
    assert list(v[strings[0]]) != list(orig[0])


@pytest.mark.parametrize("text", ["apple and orange"])
def test_vectors_token_vector(tokenizer_v, vectors, text):
    doc = tokenizer_v(text)
    assert vectors[0] == (doc[0].text, list(doc[0].vector))
    assert vectors[1] == (doc[2].text, list(doc[2].vector))


@pytest.mark.parametrize("text", ["apple"])
def test_vectors__ngrams_word(ngrams_vocab, ngrams_vectors, text):
    assert list(ngrams_vocab.get_vector(text)) == list(ngrams_vectors[0][1])


@pytest.mark.parametrize("text", ["applpie"])
def test_vectors__ngrams_subword(ngrams_vocab, ngrams_vectors, text):
    truth = list(ngrams_vocab.get_vector(text, 1, 6))
    test = list(
        [
            (
                ngrams_vectors[1][1][i]
                + ngrams_vectors[2][1][i]
                + ngrams_vectors[3][1][i]
            )
            / 3
            for i in range(len(ngrams_vectors[1][1]))
        ]
    )
    eps = [abs(truth[i] - test[i]) for i in range(len(truth))]
    for i in eps:
        assert i < 1e-6


@pytest.mark.parametrize("text", ["apple", "orange"])
def test_vectors_lexeme_vector(vocab, text):
    lex = vocab[text]
    assert list(lex.vector)
    assert lex.vector_norm


@pytest.mark.parametrize("text", [["apple", "and", "orange"]])
def test_vectors_doc_vector(vocab, text):
    doc = Doc(vocab, words=text)
    assert list(doc.vector)
    assert doc.vector_norm


@pytest.mark.parametrize("text", [["apple", "and", "orange"]])
def test_vectors_span_vector(vocab, text):
    span = Doc(vocab, words=text)[0:2]
    assert list(span.vector)
    assert span.vector_norm


@pytest.mark.parametrize("text", ["apple orange"])
def test_vectors_token_token_similarity(tokenizer_v, text):
    doc = tokenizer_v(text)
    assert doc[0].similarity(doc[1]) == doc[1].similarity(doc[0])
    assert -1.0 < doc[0].similarity(doc[1]) < 1.0


@pytest.mark.parametrize("text1,text2", [("apple", "orange")])
def test_vectors_token_lexeme_similarity(tokenizer_v, vocab, text1, text2):
    token = tokenizer_v(text1)
    lex = vocab[text2]
    assert token.similarity(lex) == lex.similarity(token)
    assert -1.0 < token.similarity(lex) < 1.0


@pytest.mark.parametrize("text", [["apple", "orange", "juice"]])
def test_vectors_token_span_similarity(vocab, text):
    doc = Doc(vocab, words=text)
    assert doc[0].similarity(doc[1:3]) == doc[1:3].similarity(doc[0])
    assert -1.0 < doc[0].similarity(doc[1:3]) < 1.0


@pytest.mark.parametrize("text", [["apple", "orange", "juice"]])
def test_vectors_token_doc_similarity(vocab, text):
    doc = Doc(vocab, words=text)
    assert doc[0].similarity(doc) == doc.similarity(doc[0])
    assert -1.0 < doc[0].similarity(doc) < 1.0


@pytest.mark.parametrize("text", [["apple", "orange", "juice"]])
def test_vectors_lexeme_span_similarity(vocab, text):
    doc = Doc(vocab, words=text)
    lex = vocab[text[0]]
    assert lex.similarity(doc[1:3]) == doc[1:3].similarity(lex)
    assert -1.0 < doc.similarity(doc[1:3]) < 1.0


@pytest.mark.parametrize("text1,text2", [("apple", "orange")])
def test_vectors_lexeme_lexeme_similarity(vocab, text1, text2):
    lex1 = vocab[text1]
    lex2 = vocab[text2]
    assert lex1.similarity(lex2) == lex2.similarity(lex1)
    assert -1.0 < lex1.similarity(lex2) < 1.0


@pytest.mark.parametrize("text", [["apple", "orange", "juice"]])
def test_vectors_lexeme_doc_similarity(vocab, text):
    doc = Doc(vocab, words=text)
    lex = vocab[text[0]]
    assert lex.similarity(doc) == doc.similarity(lex)
    assert -1.0 < lex.similarity(doc) < 1.0


@pytest.mark.parametrize("text", [["apple", "orange", "juice"]])
def test_vectors_span_span_similarity(vocab, text):
    doc = Doc(vocab, words=text)
    with pytest.warns(UserWarning):
        assert doc[0:2].similarity(doc[1:3]) == doc[1:3].similarity(doc[0:2])
        assert -1.0 < doc[0:2].similarity(doc[1:3]) < 1.0


@pytest.mark.parametrize("text", [["apple", "orange", "juice"]])
def test_vectors_span_doc_similarity(vocab, text):
    doc = Doc(vocab, words=text)
    with pytest.warns(UserWarning):
        assert doc[0:2].similarity(doc) == doc.similarity(doc[0:2])
        assert -1.0 < doc[0:2].similarity(doc) < 1.0


@pytest.mark.parametrize(
    "text1,text2", [(["apple", "and", "apple", "pie"], ["orange", "juice"])]
)
def test_vectors_doc_doc_similarity(vocab, text1, text2):
    doc1 = Doc(vocab, words=text1)
    doc2 = Doc(vocab, words=text2)
    assert doc1.similarity(doc2) == doc2.similarity(doc1)
    assert -1.0 < doc1.similarity(doc2) < 1.0


def test_vocab_add_vector():
    vocab = Vocab()
    data = numpy.ndarray((5, 3), dtype="f")
    data[0] = 1.0
    data[1] = 2.0
    vocab.set_vector("cat", data[0])
    vocab.set_vector("dog", data[1])
    cat = vocab["cat"]
    assert list(cat.vector) == [1.0, 1.0, 1.0]
    dog = vocab["dog"]
    assert list(dog.vector) == [2.0, 2.0, 2.0]


def test_vocab_prune_vectors():
    vocab = Vocab()
    _ = vocab["cat"]  # noqa: F841
    _ = vocab["dog"]  # noqa: F841
    _ = vocab["kitten"]  # noqa: F841
    data = numpy.ndarray((5, 3), dtype="f")
    data[0] = 1.0
    data[1] = 2.0
    data[2] = 1.1
    vocab.set_vector("cat", data[0])
    vocab.set_vector("dog", data[1])
    vocab.set_vector("kitten", data[2])

    remap = vocab.prune_vectors(2)
    assert list(remap.keys()) == ["kitten"]
    neighbour, similarity = list(remap.values())[0]
    assert neighbour == "cat", remap
    assert_allclose(similarity, cosine(data[0], data[2]), atol=1e-6)
