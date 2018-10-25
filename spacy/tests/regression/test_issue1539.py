'''Ensure vectors.resize() doesn't try to modify dictionary during iteration.'''
from __future__ import unicode_literals

from ...vectors import Vectors


def test_issue1539():
    v = Vectors(shape=(10, 10), keys=[5,3,98,100])
    v.resize((100,100))

