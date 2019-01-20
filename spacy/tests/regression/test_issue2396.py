# coding: utf-8
from __future__ import unicode_literals

from ..util import get_doc

import pytest
import numpy
from numpy.testing import assert_array_equal


@pytest.mark.parametrize('words,heads,matrix', [
    (
        'She created a test for spacy'.split(),
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
def test_issue2396(en_vocab, words, heads, matrix):
    doc = get_doc(en_vocab, words=words, heads=heads)

    span = doc[:]
    assert_array_equal(doc.get_lca_matrix(), matrix)
    assert_array_equal(span.get_lca_matrix(), matrix)


