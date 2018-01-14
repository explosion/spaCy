'''Test vocab.set_vector also adds the word to the vocab.'''
from __future__ import unicode_literals
from ...vocab import Vocab

import numpy 


def test_issue1807():
    vocab = Vocab()
    arr = numpy.ones((50,), dtype='f')
    assert 'hello' not in vocab
    vocab.set_vector('hello', arr)
    assert 'hello' in vocab

