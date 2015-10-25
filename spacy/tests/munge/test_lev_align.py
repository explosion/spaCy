"""Find the min-cost alignment between two tokenizations"""
from spacy.gold import _min_edit_path as min_edit_path
from spacy.gold import align


def test_edit_path():
    cand = ["U.S", ".", "policy"]
    gold = ["U.S.", "policy"]
    assert min_edit_path(cand, gold) == (0, 'MDM')
    cand = ["U.N", ".", "policy"]
    gold = ["U.S.", "policy"]
    assert min_edit_path(cand, gold) == (1, 'SDM')
    cand = ["The", "cat", "sat", "down"]
    gold = ["The", "cat", "sat", "down"]
    assert min_edit_path(cand, gold) == (0, 'MMMM')
    cand = ["cat", "sat", "down"]
    gold = ["The", "cat", "sat", "down"]
    assert min_edit_path(cand, gold) == (1, 'IMMM')
    cand = ["The", "cat", "down"]
    gold = ["The", "cat", "sat", "down"]
    assert min_edit_path(cand, gold) == (1, 'MMIM')
    cand = ["The", "cat", "sag", "down"]
    gold = ["The", "cat", "sat", "down"]
    assert min_edit_path(cand, gold) == (1, 'MMSM')
    cand = ["your", "stuff"]
    gold = ["you", "r", "stuff"]
    assert min_edit_path(cand, gold) in [(2, 'ISM'), (2, 'SIM')]


def test_align():
    cand = ["U.S", ".", "policy"]
    gold = ["U.S.", "policy"]
    assert align(cand, gold) == [0, None, 1]
    cand = ["your", "stuff"]
    gold = ["you", "r", "stuff"]
    assert align(cand, gold) == [None, 2]
    cand = [u'i', u'like', u'2', u'guys', u'   ', u'well', u'id', u'just',
            u'come', u'straight', u'out']
    gold = [u'i', u'like', u'2', u'guys', u'well', u'i', u'd', u'just', u'come',
            u'straight', u'out']
    assert align(cand, gold) == [0, 1, 2, 3, None, 4, None, 7, 8, 9, 10]

