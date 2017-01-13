# coding: utf-8
from __future__ import unicode_literals

from ...tokens import Doc
from ..util import get_doc

import pytest


def test_serialize_io_read_write(en_vocab, text_file_b):
    text1 = ["This", "is", "a", "simple", "test", ".", "With", "a", "couple", "of", "sentences", "."]
    text2 = ["This", "is", "another", "test", "document", "."]

    doc1 = get_doc(en_vocab, text1)
    doc2 = get_doc(en_vocab, text2)
    text_file_b.write(doc1.to_bytes())
    text_file_b.write(doc2.to_bytes())
    text_file_b.seek(0)
    bytes1, bytes2 = Doc.read_bytes(text_file_b)
    result1 = get_doc(en_vocab).from_bytes(bytes1)
    result2 = get_doc(en_vocab).from_bytes(bytes2)
    assert result1.text_with_ws == doc1.text_with_ws
    assert result2.text_with_ws == doc2.text_with_ws


def test_serialize_io_left_right(en_vocab):
    text = ["This", "is", "a", "simple", "test", ".", "With", "a",  "couple", "of", "sentences", "."]
    doc = get_doc(en_vocab, text)
    result = Doc(en_vocab).from_bytes(doc.to_bytes())

    for token in result:
        assert token.head.i == doc[token.i].head.i
        if token.head is not token:
            assert token.i in [w.i for w in token.head.children]
        for child in token.lefts:
            assert child.head.i == token.i
        for child in token.rights:
            assert child.head.i == token.i


@pytest.mark.models
def test_lemmas(EN):
    text = "The geese are flying"
    doc = EN(text)
    result = Doc(doc.vocab).from_bytes(doc.to_bytes())
    assert result[1].lemma_ == 'goose'
    assert result[2].lemma_ == 'be'
    assert result[3].lemma_ == 'fly'
