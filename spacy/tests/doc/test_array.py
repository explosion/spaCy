# coding: utf-8
from __future__ import unicode_literals

from ...attrs import ORTH, SHAPE, POS, DEP
from ..util import get_doc

import pytest


def test_doc_array_attr_of_token(en_tokenizer, en_vocab):
    text = "An example sentence"
    tokens = en_tokenizer(text)
    example = tokens.vocab["example"]
    assert example.orth != example.shape
    feats_array = tokens.to_array((ORTH, SHAPE))
    assert feats_array[0][0] != feats_array[0][1]
    assert feats_array[0][0] != feats_array[0][1]


def test_doc_stringy_array_attr_of_token(en_tokenizer, en_vocab):
    text = "An example sentence"
    tokens = en_tokenizer(text)
    example = tokens.vocab["example"]
    assert example.orth != example.shape
    feats_array = tokens.to_array((ORTH, SHAPE))
    feats_array_stringy = tokens.to_array(("ORTH", "SHAPE"))
    assert feats_array_stringy[0][0] == feats_array[0][0]
    assert feats_array_stringy[0][1] == feats_array[0][1]


def test_doc_scalar_attr_of_token(en_tokenizer, en_vocab):
    text = "An example sentence"
    tokens = en_tokenizer(text)
    example = tokens.vocab["example"]
    assert example.orth != example.shape
    feats_array = tokens.to_array(ORTH)
    assert feats_array.shape == (3,)


def test_doc_array_tag(en_tokenizer):
    text = "A nice sentence."
    pos = ['DET', 'ADJ', 'NOUN', 'PUNCT']
    tokens = en_tokenizer(text)
    doc = get_doc(tokens.vocab, [t.text for t in tokens], pos=pos)
    assert doc[0].pos != doc[1].pos != doc[2].pos != doc[3].pos
    feats_array = doc.to_array((ORTH, POS))
    assert feats_array[0][1] == doc[0].pos
    assert feats_array[1][1] == doc[1].pos
    assert feats_array[2][1] == doc[2].pos
    assert feats_array[3][1] == doc[3].pos


def test_doc_array_dep(en_tokenizer):
    text = "A nice sentence."
    deps = ['det', 'amod', 'ROOT', 'punct']
    tokens = en_tokenizer(text)
    doc = get_doc(tokens.vocab, [t.text for t in tokens], deps=deps)
    feats_array = doc.to_array((ORTH, DEP))
    assert feats_array[0][1] == doc[0].dep
    assert feats_array[1][1] == doc[1].dep
    assert feats_array[2][1] == doc[2].dep
    assert feats_array[3][1] == doc[3].dep
