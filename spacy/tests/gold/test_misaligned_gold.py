'''Test logic for mapping annotations when the gold parse and the doc don't
align in tokenization.'''
from __future__ import unicode_literals
import pytest
from ...tokens import Doc
from ...gold import GoldParse
from ...gold import _flatten_fused_heads
from ...vocab import Vocab

@pytest.mark.parametrize('fused,flat', [
    ([ [(0, 1), 1], 1], [1, 2, 2]),
    ([1, 1, [1, 3], 1], [1, 1, 1, 4, 1])
])
def test_flatten_fused_heads(fused, flat):
    assert _flatten_fused_heads(fused) == flat


def test_over_segmented():
    doc = Doc(Vocab(), words=['a', 'b', 'c'])
    gold = GoldParse(doc, words=['ab', 'c'], heads=[1,1])
    assert gold.heads == [1, 2, 2]
    assert gold.labels == ['subtok', None, None]

def test_under_segmented():
    doc = Doc(Vocab(), words=['ab', 'c'])
    gold = GoldParse(doc, words=['a', 'b', 'c'], heads=[2,2,2])
    assert gold.heads == [[1,1], 1]
    assert gold.labels == [[None, None], None]
