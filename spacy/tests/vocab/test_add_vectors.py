# coding: utf-8
from __future__ import unicode_literals

import numpy
import pytest


@pytest.mark.parametrize('text', ["Hello"])
def test_vocab_add_vector(en_vocab, text):
    en_vocab.resize_vectors(10)
    lex = en_vocab[text]
    lex.vector = numpy.ndarray((10,), dtype='float32')
    lex = en_vocab[text]
    assert lex.vector.shape == (10,)
