from __future__ import unicode_literals
import pytest
import gc

from spacy.en import English


def get_orphan_token(text, i):
    nlp = English()
    tokens = nlp(text)
    gc.collect()
    token = tokens[i]
    del tokens
    return token


def test_orphan():
    orphan = get_orphan_token('An orphan token', 1)
    gc.collect()
    dummy = get_orphan_token('Load and flush the memory', 0)
    dummy = get_orphan_token('Load again...', 0)
    assert orphan.orth_ == 'orphan'
    assert orphan.pos_ == 'ADJ'
    assert orphan.head.orth_ == 'token'
