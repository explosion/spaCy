# coding: utf8
from __future__ import unicode_literals

from ...vectors import Vectors

def test_issue1518():
    '''Test vectors.resize() works.'''
    vectors = Vectors(shape=(10, 10))
    vectors.add(u'hello', row=2)
    vectors.resize((5, 9))
