import numpy

import spacy.en


def test_add_vector():
    vocab = spacy.en.English.Defaults.create_vocab()
    vocab.resize_vectors(10)
    lex = vocab[u'Hello']
    lex.vector = numpy.ndarray((10,), dtype='float32')
    lex = vocab[u'Hello']
    assert lex.vector.shape == (10,)
