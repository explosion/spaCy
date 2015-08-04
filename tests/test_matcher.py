from __future__ import unicode_literals
import pytest

from spacy.matcher import *


class MockToken(object):
    def __init__(self, i, string):
        self.i = i
        self.orth_ = string


def make_tokens(string):
    return [MockToken(i, s) for i, s in enumerate(string.split())]


@pytest.fixture
def matcher():
    specs = []
    for string in ['JavaScript', 'Google Now', 'Java']:
        spec = tuple([[('orth_', orth)] for orth in string.split()])
        specs.append((spec, 'product'))
    return Matcher(specs)


def test_compile(matcher):
    assert len(matcher.start_states) == 3


def test_no_match(matcher):
    tokens = make_tokens('I like cheese')
    assert matcher(tokens) == []


def test_match_start(matcher):
    tokens = make_tokens('JavaScript is good')
    assert matcher(tokens) == [('product', 0, 1)]


def test_match_end(matcher):
    tokens = make_tokens('I like Java')
    assert matcher(tokens) == [('product', 2, 3)]


def test_match_middle(matcher):
    tokens = make_tokens('I like Google Now best')
    assert matcher(tokens) == [('product', 2, 4)]


def test_match_multi(matcher):
    tokens = make_tokens('I like Google Now and Java best')
    assert matcher(tokens) == [('product', 2, 4), ('product', 5, 6)]
