# coding: utf8
from __future__ import unicode_literals

import numpy
from spacy.vectors import Vectors
from spacy.vocab import Vocab
from spacy.tokens import Doc
from spacy._ml import link_vectors_to_models


def test_issue2871():
    """Test that vectors recover the correct key for spaCy reserved words."""
    words = ['dog', 'cat', 'SUFFIX']
    vocab = Vocab()
    vocab.vectors.resize(shape=(3, 10))
    vector_data = numpy.zeros((3, 10), dtype='f')
    for word in words:
        _ = vocab[word]
        vocab.set_vector(word, vector_data[0])
    vocab.vectors.name = 'dummy_vectors'
    link_vectors_to_models(vocab)
    assert vocab['dog'].rank == 0
    assert vocab['cat'].rank == 1
    assert vocab['SUFFIX'].rank == 2
    assert vocab.vectors.find(key='dog') == 0
    assert vocab.vectors.find(key='cat') == 1
    assert vocab.vectors.find(key='SUFFIX') == 2
