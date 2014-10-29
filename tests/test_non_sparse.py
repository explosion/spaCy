import py.test

from spacy.orth import non_sparse
import math


def test_common_case_upper():
    cases = {'u': 0.7, 'l': 0.2, 't': 0.1}
    prob = math.log(0.1)
    assert non_sparse('usa', prob, 0, cases['u'], cases['t'], cases['l']) == 'USA'

def test_same():
    cases = {'u': 0.01, 't': 0.09, 'l': 0.9}
    prob = math.log(0.5)
    assert non_sparse('the', prob, 0, cases['u'], cases['t'], cases['l']) == 'the'

def test_common_case_lower():
    prob = math.log(0.5)
    cases = {'u': 0.01, 't': 0.09, 'l': 0.9}
    assert non_sparse('The', prob, 0, cases['u'], cases['t'], cases['l']) == 'the'

def test_shape():
    prob = math.log(0.00001)
    cases = {'u': 0.0, 't': 0.0, 'l': 0.0}
    assert non_sparse('1999', prob, 0, cases['u'], cases['t'], cases['l']) == 'dddd'
