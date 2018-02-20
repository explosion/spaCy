import pytest
from .._align import align


@pytest.mark.parametrize('string1,string2,cost', [
    (b'hello', b'hell', 1),
    (b'rat', b'cat', 1),
    (b'rat', b'rat', 0),
    (b'rat', b'catsie', 4),
    (b't', b'catsie', 5),
])
def test_align_costs(string1, string2, cost):
    output_cost, i2j, j2i, matrix = align(string1, string2)
    assert output_cost == cost


@pytest.mark.parametrize('string1,string2,i2j', [
    (b'hello', b'hell', [0,1,2,3,-1]),
    (b'rat', b'cat', [0,1,2]),
    (b'rat', b'rat', [0,1,2]),
    (b'rat', b'catsie', [0,1,2]),
    (b't', b'catsie', [2]),
])
def test_align_i2j(string1, string2, i2j):
    output_cost, output_i2j, j2i, matrix = align(string1, string2)
    assert list(output_i2j) == i2j


@pytest.mark.parametrize('string1,string2,j2i', [
    (b'hello', b'hell', [0,1,2,3]),
    (b'rat', b'cat', [0,1,2]),
    (b'rat', b'rat', [0,1,2]),
    (b'rat', b'catsie', [0,1,2, -1, -1, -1]),
    (b't', b'catsie', [-1, -1, 0, -1, -1, -1]),
])
def test_align_i2j(string1, string2, j2i):
    output_cost, output_i2j, output_j2i, matrix = align(string1, string2)
    assert list(output_j2i) == j2i
