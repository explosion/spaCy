# coding: utf-8
from __future__ import unicode_literals

import pytest
from spacy.pipeline import EntityRecognizer
from spacy.vocab import Vocab
from spacy.syntax.ner import BiluoPushDown
from spacy.gold import GoldParse
from spacy.tokens import Doc


@pytest.fixture
def vocab():
    return Vocab()


@pytest.fixture
def doc(vocab):
    return Doc(vocab, words=["Casey", "went", "to", "New", "York", "."])


@pytest.fixture
def entity_annots(doc):
    casey = doc[0:1]
    ny = doc[3:5]
    return [
        (casey.start_char, casey.end_char, "PERSON"),
        (ny.start_char, ny.end_char, "GPE"),
    ]


@pytest.fixture
def entity_types(entity_annots):
    return sorted(set([label for (s, e, label) in entity_annots]))


@pytest.fixture
def tsys(vocab, entity_types):
    actions = BiluoPushDown.get_actions(entity_types=entity_types)
    return BiluoPushDown(vocab.strings, actions)


def test_get_oracle_moves(tsys, doc, entity_annots):
    gold = GoldParse(doc, entities=entity_annots)
    tsys.preprocess_gold(gold)
    act_classes = tsys.get_oracle_sequence(doc, gold)
    names = [tsys.get_class_name(act) for act in act_classes]
    assert names == ["U-PERSON", "O", "O", "B-GPE", "L-GPE", "O"]


def test_get_oracle_moves_negative_entities(tsys, doc, entity_annots):
    entity_annots = [(s, e, "!" + label) for s, e, label in entity_annots]
    gold = GoldParse(doc, entities=entity_annots)
    for i, tag in enumerate(gold.ner):
        if tag == "L-!GPE":
            gold.ner[i] = "-"
    tsys.preprocess_gold(gold)
    act_classes = tsys.get_oracle_sequence(doc, gold)
    names = [tsys.get_class_name(act) for act in act_classes]
    assert names


def test_get_oracle_moves_negative_entities2(tsys, vocab):
    doc = Doc(vocab, words=["A", "B", "C", "D"])
    gold = GoldParse(doc, entities=[])
    gold.ner = ["B-!PERSON", "L-!PERSON", "B-!PERSON", "L-!PERSON"]
    tsys.preprocess_gold(gold)
    act_classes = tsys.get_oracle_sequence(doc, gold)
    names = [tsys.get_class_name(act) for act in act_classes]
    assert names


def test_get_oracle_moves_negative_O(tsys, vocab):
    doc = Doc(vocab, words=["A", "B", "C", "D"])
    gold = GoldParse(doc, entities=[])
    gold.ner = ["O", "!O", "O", "!O"]
    tsys.preprocess_gold(gold)
    act_classes = tsys.get_oracle_sequence(doc, gold)
    names = [tsys.get_class_name(act) for act in act_classes]
    assert names


def test_doc_add_entities_set_ents_iob(en_vocab):
    doc = Doc(en_vocab, words=["This", "is", "a", "lion"])
    ner = EntityRecognizer(en_vocab)
    ner.begin_training([])
    ner(doc)
    assert len(list(doc.ents)) == 0
    assert [w.ent_iob_ for w in doc] == (["O"] * len(doc))
    doc.ents = [(doc.vocab.strings["ANIMAL"], 3, 4)]
    assert [w.ent_iob_ for w in doc] == ["", "", "", "B"]
    doc.ents = [(doc.vocab.strings["WORD"], 0, 2)]
    assert [w.ent_iob_ for w in doc] == ["B", "I", "", ""]
