from __future__ import unicode_literals
import spacy
from spacy.vocab import Vocab
from spacy.tokens.doc import Doc
import numpy
import numpy.linalg

import pytest


def get_vector(letters):
    return numpy.asarray([ord(letter) for letter in letters], dtype='float32')


def get_cosine(vec1, vec2):
    return numpy.dot(vec1, vec2) / (numpy.linalg.norm(vec1) * numpy.linalg.norm(vec2))


@pytest.fixture(scope='module')
def en_vocab():
    vocab = spacy.get_lang_class('en').Defaults.create_vocab()
    vocab.resize_vectors(2)
    apple_ = vocab[u'apple']
    orange_ = vocab[u'orange']
    apple_.vector = get_vector('ap')
    orange_.vector = get_vector('or')
    return vocab


@pytest.fixture
def appleL(en_vocab):
   return en_vocab['apple']


@pytest.fixture
def orangeL(en_vocab):
   return en_vocab['orange']


@pytest.fixture(scope='module')
def apple_orange(en_vocab):
    return Doc(en_vocab, words=[u'apple', u'orange'])


@pytest.fixture
def appleT(apple_orange):
    return apple_orange[0]


@pytest.fixture
def orangeT(apple_orange):
    return apple_orange[1]


def test_LL_sim(appleL, orangeL):
    assert appleL.has_vector
    assert orangeL.has_vector
    assert appleL.vector_norm != 0
    assert orangeL.vector_norm != 0
    assert appleL.vector[0] != orangeL.vector[0] and appleL.vector[1] != orangeL.vector[1]
    assert numpy.isclose(
            appleL.similarity(orangeL),
            get_cosine(get_vector('ap'), get_vector('or')))
    assert numpy.isclose(
            orangeL.similarity(appleL),
            appleL.similarity(orangeL))


def test_TT_sim(appleT, orangeT):
    assert appleT.has_vector
    assert orangeT.has_vector
    assert appleT.vector_norm != 0
    assert orangeT.vector_norm != 0
    assert appleT.vector[0] != orangeT.vector[0] and appleT.vector[1] != orangeT.vector[1]
    assert numpy.isclose(
            appleT.similarity(orangeT),
            get_cosine(get_vector('ap'), get_vector('or')))
    assert numpy.isclose(
            orangeT.similarity(appleT),
            appleT.similarity(orangeT))


def test_TD_sim(apple_orange, appleT):
    assert apple_orange.similarity(appleT) == appleT.similarity(apple_orange)

def test_DS_sim(apple_orange, appleT):
    span = apple_orange[:2]
    assert apple_orange.similarity(span) == 1.0
    assert span.similarity(apple_orange) == 1.0


def test_TS_sim(apple_orange, appleT):
    span = apple_orange[:2]
    assert span.similarity(appleT) == appleT.similarity(span)


