import pytest

from spacy._hashing import PointerHash
import random


def test_insert():
    h = PointerHash()
    assert h[1] is None
    h[1] = 5
    assert h[1] == 5
    h[2] = 6
    assert h[1] == 5
    assert h[2] == 6

def test_resize():
    h = PointerHash(4)
    for i in range(1, 100):
        value = int(i * (random.random() + 1))
        h[i] = value
