from __future__ import unicode_literals
import pytest
from numpy.testing import assert_array_equal
from .._align import levenshtein_align, multi_align, Alignment
from .._align import _get_regions, _get_many2one


@pytest.mark.parametrize('string1,string2,cost', [
    ('hello', 'hell', 1),
    ('rat', 'cat', 1),
    ('rat', 'rat', 0),
    ('rat', 'catsie', 4),
    ('t', 'catsie', 5),
])
def test_align_costs(string1, string2, cost):
    output_cost, i2j, j2i, matrix = levenshtein_align(string1, string2)
    assert output_cost == cost


@pytest.mark.parametrize('string1,string2,i2j', [
    ('hello', 'hell', [0,1,2,3,-1]),
    ('rat', 'cat', [0,1,2]),
    ('rat', 'rat', [0,1,2]),
    ('rat', 'catsie', [0,1,2]),
    ('t', 'catsie', [2]),
])
def test_align_i2j(string1, string2, i2j):
    output_cost, output_i2j, j2i, matrix = levenshtein_align(string1, string2)
    assert list(output_i2j) == i2j


@pytest.mark.parametrize('string1,string2,j2i', [
    ('hello', 'hell', [0,1,2,3]),
    ('rat', 'cat', [0,1,2]),
    ('rat', 'rat', [0,1,2]),
    ('rat', 'catsie', [0,1,2, -1, -1, -1]),
    ('t', 'catsie', [-1, -1, 0, -1, -1, -1]),
])
def test_align_i2j(string1, string2, j2i):
    output_cost, output_i2j, output_j2i, matrix = levenshtein_align(string1, string2)
    assert list(output_j2i) == j2i

def test_align_strings():
    words1 = ['hello', 'this', 'is', 'test!']
    words2 = ['hellothis', 'is', 'test', '!']
    cost, i2j, j2i, matrix = levenshtein_align(words1, words2)
    assert cost == 4
    assert list(i2j) == [-1, -1, 1, -1]
    assert list(j2i) == [-1, 2, -1, -1]

def test_levenshtein_align_is_symmetric():
    words1 = ['a', 'bc', 'd']
    words2 = ['a', 'b', 'c', 'd']
    i_lengths = [len(w) for w in words1] 
    j_lengths = [len(w) for w in words2] 
    cost, i2j, j2i, matrix = levenshtein_align(words1, words2)
    new_cost, new_j2i, new_i2j, new_matrix = levenshtein_align(words2, words1)
    assert cost == new_cost
    assert list(i2j) == list(new_i2j)
    assert list(j2i) == list(new_j2i)
    assert_array_equal(matrix, new_matrix.T)

 
def test_get_many_to_one_undersegment():
    words1 = ['a', 'bc', 'd']
    words2 = ['a', 'b', 'c', 'd']
    i_lengths = [len(w) for w in words1] 
    j_lengths = [len(w) for w in words2] 
    cost, i2j, j2i, matrix = levenshtein_align(words1, words2)
    i2j_miss = _get_regions(i2j, i_lengths)
    j2i_miss = _get_regions(j2i, j_lengths)
    i2j_many2one = _get_many2one(i2j_miss, j2i_miss, i_lengths, j_lengths)
    assert i2j_many2one == {}
    j2i_many2one = _get_many2one(j2i_miss, i2j_miss, j_lengths, i_lengths)
    assert j2i_many2one == {1: 1, 2: 1}


def test_align_many_to_one():
    words1 = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    words2 = ['ab', 'bc', 'e', 'fg', 'h']
    cost, i2j, j2i, matrix = levenshtein_align(words1, words2)
    assert list(i2j) == [-1, -1, -1, -1, 2, -1, -1, 4]
    lengths1 = [len(w) for w in words1]
    lengths2 = [len(w) for w in words2]
    i2j_miss = _get_regions(i2j, lengths1)
    j2i_miss = _get_regions(j2i, lengths2)
    i2j_multi = _get_many2one(i2j_miss, j2i_miss, lengths1, lengths2)
    assert i2j_multi[0] == 0
    assert i2j_multi[1] == 0
    assert i2j_multi[2] == 1
    assert i2j_multi[3] == 1
    assert i2j_multi[3] == 1
    assert i2j_multi[5] == 3
    assert i2j_multi[6] == 3


def test_alignment_class_oversegment():
    words1 = ['a', 'b', 'c', 'd']
    words2 = ['a', 'bc', 'd']
    A = Alignment(words1, words2)
    B = Alignment(words2, words1)
    assert A._y2t == [0, (1, 0), (1, 1), 2]
    assert A._t2y == [0, [1, 2], 3]
 

def test_alignment_class_undersegment():
    words1 = ['a', 'bc', 'd']
    words2 = ['a', 'b', 'c', 'd']
    A = Alignment(words1, words2)
    assert A._y2t == [0, [1, 2], 3]
    assert A._t2y == [0, (1, 0), (1, 1), 2]
 

@pytest.mark.parametrize('fused,flat', [
    ([ [(0, 1), 1], 1], [1, 2, 2]),
    ([1, 1, [1, 3], 1], [1, 1, 1, 4, 1])
])
def test_flatten_fused_heads(fused, flat):
    assert Alignment.flatten(fused) == flat


