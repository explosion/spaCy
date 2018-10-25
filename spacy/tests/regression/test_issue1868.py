'''Test Vocab.__contains__ works with int keys'''
from __future__ import unicode_literals

from ... vocab import Vocab

def test_issue1868():
    vocab = Vocab()
    lex = vocab['hello']
    assert lex.orth in vocab
    assert lex.orth_ in vocab
    assert 'some string' not in vocab
    int_id = vocab.strings.add('some string')
    assert int_id not in vocab
