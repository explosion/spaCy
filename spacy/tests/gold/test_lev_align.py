# coding: utf-8
"""Find the min-cost alignment between two tokenizations"""

from __future__ import unicode_literals

from ...gold import _min_edit_path as min_edit_path
from ...gold import align

import pytest


@pytest.mark.parametrize('cand,gold,path', [
    (["U.S", ".", "policy"], ["U.S.", "policy"], (0, 'MDM')),
    (["U.N", ".", "policy"], ["U.S.", "policy"], (1, 'SDM')),
    (["The", "cat", "sat", "down"], ["The", "cat", "sat", "down"], (0, 'MMMM')),
    (["cat", "sat", "down"], ["The", "cat", "sat", "down"], (1, 'IMMM')),
    (["The", "cat", "down"], ["The", "cat", "sat", "down"], (1, 'MMIM')),
    (["The", "cat", "sag", "down"], ["The", "cat", "sat", "down"], (1, 'MMSM'))])
def test_gold_lev_align_edit_path(cand, gold, path):
    assert min_edit_path(cand, gold) == path


def test_gold_lev_align_edit_path2():
    cand = ["your", "stuff"]
    gold = ["you", "r", "stuff"]
    assert min_edit_path(cand, gold) in [(2, 'ISM'), (2, 'SIM')]


@pytest.mark.parametrize('cand,gold,result', [
    (["U.S", ".", "policy"], ["U.S.", "policy"], [0, None, 1]),
    (["your", "stuff"], ["you", "r", "stuff"], [None, 2]),
    (["i", "like", "2", "guys", "   ", "well", "id", "just", "come", "straight", "out"],
     ["i", "like", "2", "guys", "well", "i", "d", "just", "come", "straight", "out"],
     [0, 1, 2, 3, None, 4, None, 7, 8, 9, 10])])
def test_gold_lev_align(cand, gold, result):
    assert align(cand, gold) == result
