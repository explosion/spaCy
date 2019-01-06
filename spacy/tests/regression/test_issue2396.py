# coding: utf-8
from __future__ import unicode_literals

from ..util import get_doc

import pytest
import numpy

@pytest.mark.parametrize('sentence,heads,matrix', [
    (
        'She created a test for spacy',
        [1, 0, 1, -2, -1, -1],
        numpy.array([
            [0, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1],
            [1, 1, 2, 3, 3, 3],
            [1, 1, 3, 3, 3, 3],
            [1, 1, 3, 3, 4, 4],
            [1, 1, 3, 3, 4, 5]], dtype=numpy.int32)
    )
    ])
def test_issue2396(en_tokenizer, sentence, heads, matrix):
    tokens = en_tokenizer(sentence)
    doc = get_doc(tokens.vocab, [t.text for t in tokens], heads=heads)
    span = doc[:]
    assert (doc.get_lca_matrix() == matrix).all()
    assert (span.get_lca_matrix() == matrix).all()


