# coding: utf-8
from __future__ import unicode_literals

import pytest
from spacy.tokens import Doc
from spacy.attrs import ORTH, SHAPE, POS, DEP

from ..util import get_doc


def test_doc_array_attr_of_token(en_vocab):
    doc = Doc(en_vocab, words=["An", "example", "sentence"])
    example = doc.vocab["example"]
    assert example.orth != example.shape
    feats_array = doc.to_array((ORTH, SHAPE))
    assert feats_array[0][0] != feats_array[0][1]
    assert feats_array[0][0] != feats_array[0][1]


def test_doc_stringy_array_attr_of_token(en_vocab):
    doc = Doc(en_vocab, words=["An", "example", "sentence"])
    example = doc.vocab["example"]
    assert example.orth != example.shape
    feats_array = doc.to_array((ORTH, SHAPE))
    feats_array_stringy = doc.to_array(("ORTH", "SHAPE"))
    assert feats_array_stringy[0][0] == feats_array[0][0]
    assert feats_array_stringy[0][1] == feats_array[0][1]


def test_doc_scalar_attr_of_token(en_vocab):
    doc = Doc(en_vocab, words=["An", "example", "sentence"])
    example = doc.vocab["example"]
    assert example.orth != example.shape
    feats_array = doc.to_array(ORTH)
    assert feats_array.shape == (3,)


def test_doc_array_tag(en_vocab):
    words = ["A", "nice", "sentence", "."]
    pos = ["DET", "ADJ", "NOUN", "PUNCT"]
    doc = get_doc(en_vocab, words=words, pos=pos)
    assert doc[0].pos != doc[1].pos != doc[2].pos != doc[3].pos
    feats_array = doc.to_array((ORTH, POS))
    assert feats_array[0][1] == doc[0].pos
    assert feats_array[1][1] == doc[1].pos
    assert feats_array[2][1] == doc[2].pos
    assert feats_array[3][1] == doc[3].pos


def test_doc_array_dep(en_vocab):
    words = ["A", "nice", "sentence", "."]
    deps = ["det", "amod", "ROOT", "punct"]
    doc = get_doc(en_vocab, words=words, deps=deps)
    feats_array = doc.to_array((ORTH, DEP))
    assert feats_array[0][1] == doc[0].dep
    assert feats_array[1][1] == doc[1].dep
    assert feats_array[2][1] == doc[2].dep
    assert feats_array[3][1] == doc[3].dep


@pytest.mark.parametrize("attrs", [["ORTH", "SHAPE"], "IS_ALPHA"])
def test_doc_array_to_from_string_attrs(en_vocab, attrs):
    """Test that both Doc.to_array and Doc.from_array accept string attrs,
    as well as single attrs and sequences of attrs.
    """
    words = ["An", "example", "sentence"]
    doc = Doc(en_vocab, words=words)
    Doc(en_vocab, words=words).from_array(attrs, doc.to_array(attrs))


def test_doc_array_idx(en_vocab):
    """Test that Doc.to_array can retrieve token start indices"""
    words = ["An", "example", "sentence"]
    doc = Doc(en_vocab, words=words)
    offsets = Doc(en_vocab, words=words).to_array("IDX")

    assert offsets[0] == 0
    assert offsets[1] == 3
    assert offsets[2] == 11


def test_doc_from_array_heads_in_bounds(en_vocab):
    """Test that Doc.from_array doesn't set heads that are out of bounds."""
    words = ["This", "is", "a", "sentence", "."]
    doc = Doc(en_vocab, words=words)
    for token in doc:
        token.head = doc[0]

    # correct
    arr = doc.to_array(["HEAD"])
    doc_from_array = Doc(en_vocab, words=words)
    doc_from_array.from_array(["HEAD"], arr)

    # head before start
    arr = doc.to_array(["HEAD"])
    arr[0] = -1
    doc_from_array = Doc(en_vocab, words=words)
    with pytest.raises(ValueError):
        doc_from_array.from_array(["HEAD"], arr)

    # head after end
    arr = doc.to_array(["HEAD"])
    arr[0] = 5
    doc_from_array = Doc(en_vocab, words=words)
    with pytest.raises(ValueError):
        doc_from_array.from_array(["HEAD"], arr)
