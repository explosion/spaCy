# coding: utf-8
from __future__ import unicode_literals

from spacy.pipeline import EntityRecognizer
from spacy.tokens import Span
import pytest

from ..util import get_doc


def test_doc_add_entities_set_ents_iob(en_vocab):
    text = ["This", "is", "a", "lion"]
    doc = get_doc(en_vocab, text)
    ner = EntityRecognizer(en_vocab)
    ner.begin_training([])
    ner(doc)
    assert len(list(doc.ents)) == 0
    assert [w.ent_iob_ for w in doc] == (["O"] * len(doc))

    doc.ents = [(doc.vocab.strings["ANIMAL"], 3, 4)]
    assert [w.ent_iob_ for w in doc] == ["O", "O", "O", "B"]

    doc.ents = [(doc.vocab.strings["WORD"], 0, 2)]
    assert [w.ent_iob_ for w in doc] == ["B", "I", "O", "O"]


def test_ents_reset(en_vocab):
    text = ["This", "is", "a", "lion"]
    doc = get_doc(en_vocab, text)
    ner = EntityRecognizer(en_vocab)
    ner.begin_training([])
    ner(doc)
    assert [t.ent_iob_ for t in doc] == (["O"] * len(doc))
    doc.ents = list(doc.ents)
    assert [t.ent_iob_ for t in doc] == (["O"] * len(doc))


def test_add_overlapping_entities(en_vocab):
    text = ["Louisiana", "Office", "of", "Conservation"]
    doc = get_doc(en_vocab, text)
    entity = Span(doc, 0, 4, label=391)
    doc.ents = [entity]

    new_entity = Span(doc, 0, 1, label=392)
    with pytest.raises(ValueError):
        doc.ents = list(doc.ents) + [new_entity]
