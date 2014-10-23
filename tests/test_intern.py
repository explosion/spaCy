# -*- coding: utf8 -*-
from __future__ import unicode_literals

from spacy.utf8string import StringStore

import pytest

@pytest.fixture
def sstore():
    return StringStore()

def test_save_bytes(sstore):
    Hello_i = sstore[b'Hello']
    assert Hello_i == 1
    assert sstore[b'Hello'] == 1
    assert sstore[b'goodbye'] != Hello_i
    assert sstore[b'hello'] != Hello_i
    assert Hello_i == 1


def test_save_unicode(sstore):
    with pytest.raises(TypeError):
        A_i = sstore['A']


def test_zero_id(sstore):
    with pytest.raises(IndexError):
        sstore[0]

def test_retrieve_id(sstore):
    A_i = sstore[b'A']
    assert sstore.size == 1
    assert sstore[1] == b'A'
    with pytest.raises(IndexError):
        sstore[2]
