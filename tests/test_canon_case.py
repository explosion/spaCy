from __future__ import unicode_literals

import py.test

from spacy.orth import canon_case as cc

def test_nasa():
    assert cc('Nasa', 0.0, 0, {'upper': 0.6, 'title': 0.3, 'lower': 0.1}, {}) == 'NASA'


def test_john():
    assert cc('john', 0.0, 0, {'title': 0.6, 'upper': 0.3, 'lower': 0.1}, {}) == 'John'


def test_apple():
    assert cc('apple', 0.0, 0, {'lower': 0.6, 'title': 0.3, 'upper': 0.1}, {}) == 'apple'


def test_tie():
    assert cc('I', 0.0, 0, {'lower': 0.0, 'title': 0.0, 'upper': 0.0}, {}) == 'I'
