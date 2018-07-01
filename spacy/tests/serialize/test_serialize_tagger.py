# coding: utf-8
from __future__ import unicode_literals

from ..util import make_tempdir
from ...pipeline import Tagger

import pytest


@pytest.fixture
def taggers(en_vocab):
    tagger1 = Tagger(en_vocab)
    tagger2 = Tagger(en_vocab)
    tagger1.model = tagger1.Model(8)
    tagger2.model = tagger1.model
    return (tagger1, tagger2)


# This seems to be a dict ordering bug somewhere. Only failing on some platforms
@pytest.mark.xfail
def test_serialize_tagger_roundtrip_bytes(en_vocab, taggers):
    tagger1, tagger2 = taggers
    tagger1_b = tagger1.to_bytes()
    tagger2_b = tagger2.to_bytes()
    tagger1 = tagger1.from_bytes(tagger1_b)
    assert tagger1.to_bytes() == tagger1_b
    new_tagger1 = Tagger(en_vocab).from_bytes(tagger1_b)
    assert new_tagger1.to_bytes() == tagger1_b


def test_serialize_tagger_roundtrip_disk(en_vocab, taggers):
    tagger1, tagger2 = taggers
    with make_tempdir() as d:
        file_path1 = d / 'tagger1'
        file_path2 = d / 'tagger2'
        tagger1.to_disk(file_path1)
        tagger2.to_disk(file_path2)
        tagger1_d = Tagger(en_vocab).from_disk(file_path1)
        tagger2_d = Tagger(en_vocab).from_disk(file_path2)
        assert tagger1_d.to_bytes() == tagger2_d.to_bytes()
