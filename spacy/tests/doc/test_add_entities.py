# coding: utf-8
from __future__ import unicode_literals

from ...pipeline import EntityRecognizer
from ..util import get_doc

import pytest


def test_doc_add_entities_set_ents_iob(en_vocab):
    text = ["This", "is", "a", "lion"]
    doc = get_doc(en_vocab, text)
    ner = EntityRecognizer(en_vocab, features=[(2,), (3,)])
    ner(doc)

    assert len(list(doc.ents)) == 0
    assert [w.ent_iob_ for w in doc] == (['O'] * len(doc))

    doc.ents = [(doc.vocab.strings['ANIMAL'], 3, 4)]
    assert [w.ent_iob_ for w in doc] == ['O', 'O', 'O', 'B']

    doc.ents = [(doc.vocab.strings['WORD'], 0, 2)]
    assert [w.ent_iob_ for w in doc] == ['B', 'I', 'O', 'O']
