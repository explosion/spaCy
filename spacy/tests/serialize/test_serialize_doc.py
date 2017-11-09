# coding: utf-8
from __future__ import unicode_literals

from ..util import make_tempdir, get_doc
from ...tokens import Doc
from ...compat import path2str

import pytest


def test_serialize_doc_roundtrip_bytes(en_vocab):
    doc = get_doc(en_vocab, words=['hello', 'world'])
    doc_b = doc.to_bytes()
    new_doc = Doc(en_vocab).from_bytes(doc_b)
    assert new_doc.to_bytes() == doc_b


def test_serialize_doc_roundtrip_disk(en_vocab):
    doc = get_doc(en_vocab, words=['hello', 'world'])
    with make_tempdir() as d:
        file_path = d / 'doc'
        doc.to_disk(file_path)
        doc_d = Doc(en_vocab).from_disk(file_path)
        assert doc.to_bytes() == doc_d.to_bytes()


def test_serialize_doc_roundtrip_disk_str_path(en_vocab):
    doc = get_doc(en_vocab, words=['hello', 'world'])
    with make_tempdir() as d:
        file_path = d / 'doc'
        file_path = path2str(file_path)
        doc.to_disk(file_path)
        doc_d = Doc(en_vocab).from_disk(file_path)
        assert doc.to_bytes() == doc_d.to_bytes()
