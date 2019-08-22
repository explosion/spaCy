# coding: utf8
from __future__ import unicode_literals

from spacy.lang.en import English
from spacy.tokens import Doc
from spacy.vocab import Vocab


def test_issue4133(en_vocab):
    nlp = English()
    vocab_bytes = nlp.vocab.to_bytes()
    words = ["Apple", "is", "looking", "at", "buying", "a", "startup"]
    pos = ["NOUN", "VERB", "ADP", "VERB", "PROPN", "NOUN", "ADP"]
    doc = Doc(en_vocab, words=words)
    for i, token in enumerate(doc):
        token.pos_ = pos[i]

    # usually this is already True when starting from proper models instead of blank English
    doc.is_tagged = True

    doc_bytes = doc.to_bytes()

    vocab = Vocab()
    vocab = vocab.from_bytes(vocab_bytes)
    doc = Doc(vocab).from_bytes(doc_bytes)

    actual = []
    for token in doc:
        actual.append(token.pos_)

    assert actual == pos
