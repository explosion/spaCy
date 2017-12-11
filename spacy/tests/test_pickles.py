# coding: utf-8
from __future__ import unicode_literals

import pytest
import dill as pickle
import numpy

from ..vocab import Vocab
from ..attrs import NORM


@pytest.mark.parametrize('text1,text2', [('hello', 'bye')])
def test_pickle_string_store(stringstore, text1, text2):
    store1 = stringstore[text1]
    store2 = stringstore[text2]
    data = pickle.dumps(stringstore, protocol=-1)
    unpickled = pickle.loads(data)
    assert unpickled[text1] == store1
    assert unpickled[text2] == store2
    assert len(stringstore) == len(unpickled)


@pytest.mark.parametrize('text1,text2', [('dog', 'cat')])
def test_pickle_vocab(text1, text2):
    vocab = Vocab(lex_attr_getters={int(NORM): lambda string: string[:-1]})
    vocab.set_vector('dog', numpy.ones((5,), dtype='f'))
    lex1 = vocab[text1]
    lex2 = vocab[text2]
    assert lex1.norm_ == text1[:-1]
    assert lex2.norm_ == text2[:-1]
    data = pickle.dumps(vocab)
    unpickled = pickle.loads(data)
    assert unpickled[text1].orth == lex1.orth
    assert unpickled[text2].orth == lex2.orth
    assert unpickled[text1].norm == lex1.norm
    assert unpickled[text2].norm == lex2.norm
    assert unpickled[text1].norm != unpickled[text2].norm
    assert unpickled.vectors is not None
    assert list(vocab['dog'].vector) == [1.,1.,1.,1.,1.]
