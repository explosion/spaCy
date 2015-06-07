from __future__ import unicode_literals
import pytest

from spacy.en import English


@pytest.fixture
def EN():
    return English()


def test_neq(EN):
    addr = EN.vocab['Hello']
    assert EN.vocab['bye'].orth != addr.orth


def test_eq(EN):
    addr = EN.vocab['Hello']
    assert EN.vocab['Hello'].orth == addr.orth


def test_case_neq(EN):
    addr = EN.vocab['Hello']
    assert EN.vocab['hello'].orth != addr.orth


def test_punct_neq(EN):
    addr = EN.vocab['Hello']
    assert EN.vocab['Hello,'].orth != addr.orth


def test_shape_attr(EN):
    example = EN.vocab['example']
    assert example.orth != example.shape
