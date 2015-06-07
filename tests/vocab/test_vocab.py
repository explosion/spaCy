from __future__ import unicode_literals
import pytest


def test_neq(en_vocab):
    addr = en_vocab['Hello']
    assert en_vocab['bye'].orth != addr.orth


def test_eq(en_vocab):
    addr = en_vocab['Hello']
    assert en_vocab['Hello'].orth == addr.orth


def test_case_neq(en_vocab):
    addr = en_vocab['Hello']
    assert en_vocab['hello'].orth != addr.orth


def test_punct_neq(en_vocab):
    addr = en_vocab['Hello']
    assert en_vocab['Hello,'].orth != addr.orth


def test_shape_attr(en_vocab):
    example = en_vocab['example']
    assert example.orth != example.shape
