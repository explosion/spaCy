# coding: utf-8
from __future__ import unicode_literals

import pytest
from spacy.tokens import Doc
from spacy.vocab import Vocab

from ..util import get_doc, assert_docs_equal


TEXT = ["This", "is", "a", "test", "sentence", "."]
TAGS = ['DT', 'VBZ', 'DT', 'NN', 'NN', '.']
DEPS = ['nsubj', 'ROOT', 'det', 'compound', 'attr', 'punct']
ENTS = [('hi', 'PERSON', 0, 1)]


@pytest.mark.xfail
@pytest.mark.parametrize('text', ['rat'])
def test_serialize_vocab(en_vocab, text):
    text_hash = en_vocab.strings.add(text)
    vocab_bytes = en_vocab.to_bytes()
    new_vocab = Vocab().from_bytes(vocab_bytes)
    assert new_vocab.strings(text_hash) == text
