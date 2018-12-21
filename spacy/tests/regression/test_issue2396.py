# coding: utf-8
from __future__ import unicode_literals
import pytest

import numpy as np

def test_issue2396(EN):
    doc = EN('He created a test for spacy')
    right_lca_matrix = np.array([
        [0, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1],
        [1, 1, 2, 3, 3, 3],
        [1, 1, 3, 3, 3, 3],
        [1, 1, 3, 3, 4, 4],
        [1, 1, 3, 3, 4, 5]
    ], dtype=np.int32)
    lca_matrix = doc.get_lca_matrix()
    assert (lca_matrix == right_lca_matrix).all()
