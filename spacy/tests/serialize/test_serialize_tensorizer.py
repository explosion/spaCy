# coding: utf-8
from __future__ import unicode_literals

from ..util import make_tempdir
from ...pipeline import Tensorizer

import pytest


def test_serialize_tensorizer_roundtrip_bytes(en_vocab):
    tensorizer = Tensorizer(en_vocab)
    tensorizer.model = tensorizer.Model()
    tensorizer_b = tensorizer.to_bytes()
    new_tensorizer = Tensorizer(en_vocab).from_bytes(tensorizer_b)
    assert new_tensorizer.to_bytes() == tensorizer_b


def test_serialize_tensorizer_roundtrip_disk(en_vocab):
    tensorizer = Tensorizer(en_vocab)
    tensorizer.model = tensorizer.Model()
    with make_tempdir() as d:
        file_path = d / 'tensorizer'
        tensorizer.to_disk(file_path)
        tensorizer_d = Tensorizer(en_vocab).from_disk(file_path)
        assert tensorizer.to_bytes() == tensorizer_d.to_bytes()
