# coding: utf-8
from __future__ import unicode_literals

from ...serialize.packer import Packer
from ..util import get_doc, assert_docs_equal

import pytest


TEXT = ["This", "is", "a", "test", "sentence", "."]
TAGS = ['DT', 'VBZ', 'DT', 'NN', 'NN', '.']
DEPS = ['nsubj', 'ROOT', 'det', 'compound', 'attr', 'punct']
ENTS = [('hi', 'PERSON', 0, 1)]


def test_serialize_empty_doc(en_vocab):
    doc = get_doc(en_vocab)
    packer = Packer(en_vocab, {})
    b = packer.pack(doc)
    assert b == b''
    loaded = get_doc(en_vocab).from_bytes(b)
    assert len(loaded) == 0


@pytest.mark.parametrize('text', [TEXT])
def test_serialize_tokens(en_vocab, text):
    doc1 = get_doc(en_vocab, [t for t in text])
    doc2 = get_doc(en_vocab).from_bytes(doc1.to_bytes())
    assert_docs_equal(doc1, doc2)


@pytest.mark.models
@pytest.mark.parametrize('text', [TEXT])
@pytest.mark.parametrize('tags', [TAGS, []])
@pytest.mark.parametrize('deps', [DEPS, []])
@pytest.mark.parametrize('ents', [ENTS, []])
def test_serialize_tokens_ner(EN, text, tags, deps, ents):
    doc1 = get_doc(EN.vocab, [t for t in text], tags=tags, deps=deps, ents=ents)
    doc2 = get_doc(EN.vocab).from_bytes(doc1.to_bytes())
    assert_docs_equal(doc1, doc2)
