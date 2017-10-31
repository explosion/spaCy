# coding: utf-8
from __future__ import unicode_literals

import numpy
import pytest
from ...vocab import Vocab
from ..._ml import cosine


def test_vocab_add_vector():
    vocab = Vocab()
    data = numpy.ndarray((5,3), dtype='f')
    data[0] = 1.
    data[1] = 2.
    vocab.set_vector(u'cat', data[0])
    vocab.set_vector(u'dog', data[1])
    cat = vocab[u'cat']
    assert list(cat.vector) == [1., 1., 1.]
    dog = vocab[u'dog']
    assert list(dog.vector) == [2., 2., 2.]
    for lex in vocab:
        print(lex.orth_)


def test_vocab_prune_vectors():
    vocab = Vocab()
    _ = vocab[u'cat']
    _ = vocab[u'dog']
    _ = vocab[u'kitten']
    print(list(vocab.strings))
    data = numpy.ndarray((5,3), dtype='f')
    data[0] = 1.
    data[1] = 2.
    data[2] = 1.1
    vocab.set_vector(u'cat', data[0])
    vocab.set_vector(u'dog', data[1])
    vocab.set_vector(u'kitten', data[2])
    for lex in vocab:
        print(lex.orth_)

    remap = vocab.prune_vectors(2)
    assert remap == {u'kitten': (u'cat', cosine(data[0], data[2]))}
    #print(remap)
