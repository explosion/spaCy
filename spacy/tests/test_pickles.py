from __future__ import unicode_literals

import io
import pytest
import dill as pickle

from ..strings import StringStore
from ..vocab import Vocab
from ..attrs import NORM


def test_pickle_string_store():
    sstore = StringStore()
    hello = sstore['hello']
    bye = sstore['bye']
    bdata = pickle.dumps(sstore, protocol=-1)
    unpickled = pickle.loads(bdata)
    assert unpickled['hello'] == hello
    assert unpickled['bye'] == bye
    assert len(sstore) == len(unpickled)


def test_pickle_vocab():
    vocab = Vocab(lex_attr_getters={int(NORM): lambda string: string[:-1]})
    dog = vocab[u'dog']
    cat = vocab[u'cat']
    assert dog.norm_ == 'do'
    assert cat.norm_ == 'ca'

    bdata = pickle.dumps(vocab)
    unpickled = pickle.loads(bdata)

    assert unpickled[u'dog'].orth == dog.orth
    assert unpickled[u'cat'].orth == cat.orth
    assert unpickled[u'dog'].norm == dog.norm
    assert unpickled[u'cat'].norm == cat.norm
    dog_ = unpickled[u'dog']
    cat_ = unpickled[u'cat']
    assert dog_.norm != cat_.norm
