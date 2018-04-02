'''Test logic for mapping annotations when the gold parse and the doc don't
align in tokenization.'''
from __future__ import unicode_literals
import pytest
from collections import Counter
from ...tokens import Doc
from ...gold import GoldParse
from ...vocab import Vocab


def test_over_segmented():
    doc = Doc(Vocab(),  words=['a', 'b', 'c'])
    gold = GoldParse(doc, words=['ab', 'c'], heads=[1,1])
    assert gold._alignment._y2t == [(0, 0), (0, 1), 1]
    assert gold.labels == ['subtok', None, None]
    assert gold.heads == [1, 2, 2]
                       
                       
def test_under_segmented():
    doc = Doc(Vocab(),  words=['ab', 'c'])
    gold = GoldParse(doc, words=['a', 'b', 'c'], heads=[2,2,2])
    assert gold.heads == [[1,1], 1]
    assert gold.labels == [[None, None], None]
                       
def test_over_segmented_heads():
    doc = Doc(Vocab(),  words=['a', 'b', 'c', 'd', 'e'])
    gold = GoldParse(doc, words=['a', 'bc', 'd', 'e'], heads=[2,2,2,2])
    assert gold._alignment._y2t == [0, (1, 0), (1, 1), 2, 3]
    assert gold._alignment._t2y == [0, [1, 2], 3, 4]
    assert gold.labels == [None, 'subtok', None, None, None]
    assert gold.heads == [3, 2, 3, 3, 3]
 
def test_under_segmented_attach_inside_fused():
    '''Test arcs point ing into the fused token,
    e.g. "its good"    
    '''                
    doc = Doc(Vocab(), words=['ab', 'c'])
    gold = GoldParse(doc, words=['a', 'b', 'c'], heads=[1,1,1])
    assert gold.heads == [[(0, 1), (0, 1)], (0, 1)]
    assert gold.labels == [[None, None], None]
                      
