import pytest

from spacy._hashing import FixedTable


def test_insert():
    table = FixedTable(20)
    table[5] = 10
    assert table.bucket(5) == 5
    assert table[4] == 0
    assert table[5] == 10

def test_clobber():
    table = FixedTable(10)
    table[9] = 1
    assert table.bucket(9) == 9
    assert table.bucket(19) == 9

