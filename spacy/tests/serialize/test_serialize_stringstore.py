# coding: utf-8
from __future__ import unicode_literals

from ..util import make_tempdir
from ...strings import StringStore

import pytest


test_strings = [([], []), (['rats', 'are', 'cute'], ['i', 'like', 'rats'])]


@pytest.mark.parametrize('strings1,strings2', test_strings)
def test_serialize_stringstore_roundtrip_bytes(strings1,strings2):
    sstore1 = StringStore(strings=strings1)
    sstore2 = StringStore(strings=strings2)
    sstore1_b = sstore1.to_bytes()
    sstore2_b = sstore2.to_bytes()
    if strings1 == strings2:
        assert sstore1_b == sstore2_b
    else:
        assert sstore1_b != sstore2_b
    sstore1 = sstore1.from_bytes(sstore1_b)
    assert sstore1.to_bytes() == sstore1_b
    new_sstore1 = StringStore().from_bytes(sstore1_b)
    assert new_sstore1.to_bytes() == sstore1_b
    assert list(new_sstore1) == strings1


@pytest.mark.parametrize('strings1,strings2', test_strings)
def test_serialize_stringstore_roundtrip_disk(strings1,strings2):
    sstore1 = StringStore(strings=strings1)
    sstore2 = StringStore(strings=strings2)
    with make_tempdir() as d:
        file_path1 = d / 'strings1'
        file_path2 = d / 'strings2'
        sstore1.to_disk(file_path1)
        sstore2.to_disk(file_path2)
        sstore1_d = StringStore().from_disk(file_path1)
        sstore2_d = StringStore().from_disk(file_path2)
        assert list(sstore1_d) == list(sstore1)
        assert list(sstore2_d) == list(sstore2)
        if strings1 == strings2:
            assert list(sstore1_d) == list(sstore2_d)
        else:
            assert list(sstore1_d) != list(sstore2_d)
