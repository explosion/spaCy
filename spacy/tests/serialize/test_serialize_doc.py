# coding: utf-8
from __future__ import unicode_literals

import pytest
from spacy.tokens import Doc
from spacy.compat import path2str

from ..util import make_tempdir


def test_serialize_empty_doc(en_vocab):
    doc = Doc(en_vocab)
    data = doc.to_bytes()
    doc2 = Doc(en_vocab)
    doc2.from_bytes(data)
    assert len(doc) == len(doc2)
    for token1, token2 in zip(doc, doc2):
        assert token1.text == token2.text


def test_serialize_doc_roundtrip_bytes(en_vocab):
    doc = Doc(en_vocab, words=["hello", "world"])
    doc_b = doc.to_bytes()
    new_doc = Doc(en_vocab).from_bytes(doc_b)
    assert new_doc.to_bytes() == doc_b


def test_serialize_doc_roundtrip_disk(en_vocab):
    doc = Doc(en_vocab, words=["hello", "world"])
    with make_tempdir() as d:
        file_path = d / "doc"
        doc.to_disk(file_path)
        doc_d = Doc(en_vocab).from_disk(file_path)
        assert doc.to_bytes() == doc_d.to_bytes()


def test_serialize_doc_roundtrip_disk_str_path(en_vocab):
    doc = Doc(en_vocab, words=["hello", "world"])
    with make_tempdir() as d:
        file_path = d / "doc"
        file_path = path2str(file_path)
        doc.to_disk(file_path)
        doc_d = Doc(en_vocab).from_disk(file_path)
        assert doc.to_bytes() == doc_d.to_bytes()


def test_serialize_doc_exclude(en_vocab):
    doc = Doc(en_vocab, words=["hello", "world"])
    doc.user_data["foo"] = "bar"
    new_doc = Doc(en_vocab).from_bytes(doc.to_bytes())
    assert new_doc.user_data["foo"] == "bar"
    new_doc = Doc(en_vocab).from_bytes(doc.to_bytes(), exclude=["user_data"])
    assert not new_doc.user_data
    new_doc = Doc(en_vocab).from_bytes(doc.to_bytes(exclude=["user_data"]))
    assert not new_doc.user_data
    with pytest.raises(ValueError):
        doc.to_bytes(user_data=False)
    with pytest.raises(ValueError):
        Doc(en_vocab).from_bytes(doc.to_bytes(), tensor=False)
