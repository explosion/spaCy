# coding: utf-8
from __future__ import unicode_literals

from ..util import get_doc, assert_docs_equal
from ...tokens import Doc
from ...vocab import Vocab

import pytest


TEXT = ["This", "is", "a", "test", "sentence", "."]
TAGS = ['DT', 'VBZ', 'DT', 'NN', 'NN', '.']
DEPS = ['nsubj', 'ROOT', 'det', 'compound', 'attr', 'punct']
ENTS = [('hi', 'PERSON', 0, 1)]


def test_serialize_empty_doc(en_vocab):
    doc = get_doc(en_vocab)
    data = doc.to_bytes()
    doc2 = Doc(en_vocab)
    doc2.from_bytes(data)
    assert len(doc) == len(doc2)
    for token1, token2 in zip(doc, doc2):
        assert token1.text == token2.text


@pytest.mark.xfail
@pytest.mark.parametrize('text', ['rat'])
def test_serialize_vocab(en_vocab, text):
    text_hash = en_vocab.strings.add(text)
    vocab_bytes = en_vocab.to_bytes()
    new_vocab = Vocab().from_bytes(vocab_bytes)
    assert new_vocab.strings(text_hash) == text

#
#@pytest.mark.parametrize('text', [TEXT])
#def test_serialize_tokens(en_vocab, text):
#    doc1 = get_doc(en_vocab, [t for t in text])
#    doc2 = get_doc(en_vocab).from_bytes(doc1.to_bytes())
#    assert_docs_equal(doc1, doc2)
#
#
#@pytest.mark.models
#@pytest.mark.parametrize('text', [TEXT])
#@pytest.mark.parametrize('tags', [TAGS, []])
#@pytest.mark.parametrize('deps', [DEPS, []])
#@pytest.mark.parametrize('ents', [ENTS, []])
#def test_serialize_tokens_ner(EN, text, tags, deps, ents):
#    doc1 = get_doc(EN.vocab, [t for t in text], tags=tags, deps=deps, ents=ents)
#    doc2 = get_doc(EN.vocab).from_bytes(doc1.to_bytes())
#    assert_docs_equal(doc1, doc2)
