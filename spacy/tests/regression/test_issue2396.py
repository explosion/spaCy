# coding: utf-8
from __future__ import unicode_literals

from ..util import get_doc

import pytest
import numpy

@pytest.mark.parametrize('sentence,matrix', [
    (
        'She created a test for spacy',
        numpy.array([
            [0, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1],
            [1, 1, 2, 3, 3, 3],
            [1, 1, 3, 3, 3, 3],
            [1, 1, 3, 3, 4, 4],
            [1, 1, 3, 3, 4, 5]], dtype=numpy.int32)
    )
    ])
def test_issue2396(EN, sentence, matrix):
    doc = EN(sentence)
    span = doc[:]
    assert (doc.get_lca_matrix() == matrix).all()
    assert (span.get_lca_matrix() == matrix).all()


