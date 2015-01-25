# -*- coding: utf8 -*-
from __future__ import unicode_literals

from spacy.strings import StringStore

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
    Hello_i = sstore[u'Hello']
    assert Hello_i == 1
    assert sstore[u'Hello'] == 1
    assert sstore[u'goodbye'] != Hello_i
    assert sstore[u'hello'] != Hello_i
    assert Hello_i == 1


def test_retrieve_id(sstore):
    A_i = sstore[b'A']
    assert sstore.size == 1
    assert sstore[1] == 'A'
    with pytest.raises(IndexError):
        sstore[2]
