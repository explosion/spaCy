# coding: utf-8
from __future__ import unicode_literals

import pytest
from spacy._align import align, multi_align


@pytest.mark.parametrize(
    "string1,string2,cost",
    [
        ("hello", "hell", 1),
        ("rat", "cat", 1),
        ("rat", "rat", 0),
        ("rat", "catsie", 4),
        ("t", "catsie", 5),
    ],
)
def test_align_costs(string1, string2, cost):
    output_cost, i2j, j2i, matrix = align(string1, string2)
    assert output_cost == cost


@pytest.mark.parametrize(
    "string1,string2,i2j",
    [
        ("hello", "hell", [0, 1, 2, 3, -1]),
        ("rat", "cat", [0, 1, 2]),
        ("rat", "rat", [0, 1, 2]),
        ("rat", "catsie", [0, 1, 2]),
        ("t", "catsie", [2]),
    ],
)
def test_align_i2j(string1, string2, i2j):
    output_cost, output_i2j, j2i, matrix = align(string1, string2)
    assert list(output_i2j) == i2j


@pytest.mark.parametrize(
    "string1,string2,j2i",
    [
        ("hello", "hell", [0, 1, 2, 3]),
        ("rat", "cat", [0, 1, 2]),
        ("rat", "rat", [0, 1, 2]),
        ("rat", "catsie", [0, 1, 2, -1, -1, -1]),
        ("t", "catsie", [-1, -1, 0, -1, -1, -1]),
    ],
)
def test_align_i2j_2(string1, string2, j2i):
    output_cost, output_i2j, output_j2i, matrix = align(string1, string2)
    assert list(output_j2i) == j2i


def test_align_strings():
    words1 = ["hello", "this", "is", "test!"]
    words2 = ["hellothis", "is", "test", "!"]
    cost, i2j, j2i, matrix = align(words1, words2)
    assert cost == 4
    assert list(i2j) == [-1, -1, 1, -1]
    assert list(j2i) == [-1, 2, -1, -1]


def test_align_many_to_one():
    words1 = ["a", "b", "c", "d", "e", "f", "g", "h"]
    words2 = ["ab", "bc", "e", "fg", "h"]
    cost, i2j, j2i, matrix = align(words1, words2)
    assert list(i2j) == [-1, -1, -1, -1, 2, -1, -1, 4]
    lengths1 = [len(w) for w in words1]
    lengths2 = [len(w) for w in words2]
    i2j_multi, j2i_multi = multi_align(i2j, j2i, lengths1, lengths2)
    assert i2j_multi[0] == 0
    assert i2j_multi[1] == 0
    assert i2j_multi[2] == 1
    assert i2j_multi[3] == 1
    assert i2j_multi[3] == 1
    assert i2j_multi[5] == 3
    assert i2j_multi[6] == 3

    assert j2i_multi[0] == 1
    assert j2i_multi[1] == 3
