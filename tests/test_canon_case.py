from __future__ import unicode_literals

import py.test

from spacy.orth import canon_case as cc

def test_nasa():
    assert cc('Nasa', 0.6, 0.3, 0.1) == 'NASA'


def test_john():
    assert cc('john', 0.3, 0.6, 0.1) == 'John'


def test_apple():
    assert cc('apple', 0.1, 0.3, 0.6) == 'apple'


def test_tie():
    assert cc('I', 0.0, 0.0, 0.0) == 'I'
