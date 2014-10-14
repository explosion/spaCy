"""Test that tokens are created correctly for whitespace."""
from __future__ import unicode_literals

from spacy.en import EN
import pytest


def test_single_space():
    tokens = EN.tokenize('hello possums')
    assert len(tokens) == 2


def test_double_space():
    tokens = EN.tokenize('hello  possums')
    assert len(tokens) == 3
    assert tokens[1].string == ' '


def test_newline():
    tokens = EN.tokenize('hello\npossums')
    assert len(tokens) == 3


def test_newline_space():
    tokens = EN.tokenize('hello \npossums')
    assert len(tokens) == 3


def test_newline_double_space():
    tokens = EN.tokenize('hello  \npossums')
    assert len(tokens) == 3


def test_newline_space_wrap():
    tokens = EN.tokenize('hello \n possums')
    assert len(tokens) == 3


