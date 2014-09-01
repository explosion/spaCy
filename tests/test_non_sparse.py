import py.test

from spacy.orth import non_sparse
import math


def test_common_case_upper():
    cases = {'upper': 0.7, 'lower': 0.2, 'title': 0.1}
    prob = math.log(0.1)
    assert non_sparse('usa', prob, 0, cases, {}) == 'USA'

def test_same():
    cases = {'upper': 0.01, 'title': 0.09, 'lower': 0.9}
    prob = math.log(0.5)
    assert non_sparse('the', prob, 0, cases, {}) == 'the'

def test_common_case_lower():
    prob = math.log(0.5)
    cases = {'upper': 0.01, 'title': 0.09, 'lower': 0.9}
    assert non_sparse('The', prob, 0, cases, {}) == 'the'

def test_shape():
    prob = math.log(0.00001)
    cases = {'upper': 0.0, 'title': 0.0, 'lower': 0.0}
    assert non_sparse('1999', prob, 0, cases, {}) == 'dddd'
