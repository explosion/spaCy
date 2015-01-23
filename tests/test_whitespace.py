"""Test that tokens are created correctly for whitespace."""
from __future__ import unicode_literals

from spacy.en import English
import pytest


@pytest.fixture
def EN():
    return English()


def test_single_space(EN):
    tokens = EN('hello possums')
    assert len(tokens) == 2


def test_double_space(EN):
    tokens = EN('hello  possums')
    assert len(tokens) == 3
    assert tokens[1].orth_ == ' '


def test_newline(EN):
    tokens = EN('hello\npossums')
    assert len(tokens) == 3


def test_newline_space(EN):
    tokens = EN('hello \npossums')
    assert len(tokens) == 3


def test_newline_double_space(EN):
    tokens = EN('hello  \npossums')
    assert len(tokens) == 3


def test_newline_space_wrap(EN):
    tokens = EN('hello \n possums')
    assert len(tokens) == 3


