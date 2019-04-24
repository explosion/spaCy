# coding: utf8
from __future__ import unicode_literals

from spacy.util import decaying


def test_issue3447():
    sizes = decaying(10.0, 1.0, 0.5)
    size = next(sizes)
    assert size == 10.0
    size = next(sizes)
    assert size == 10.0 - 0.5
    size = next(sizes)
    assert size == 10.0 - 0.5 - 0.5
