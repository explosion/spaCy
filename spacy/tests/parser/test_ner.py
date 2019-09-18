# coding: utf-8
from __future__ import unicode_literals

import pytest
from spacy.lang.en import English

from spacy.pipeline import EntityRecognizer, EntityRuler
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


def test_accept_blocked_token():
    """Test succesful blocking of tokens to be in an entity."""
    # 1. test normal behaviour
    nlp1 = English()
    doc1 = nlp1("I live in New York")
    ner1 = EntityRecognizer(doc1.vocab)
    assert [token.ent_iob_ for token in doc1] == ["", "", "", "", ""]
    assert [token.ent_type_ for token in doc1] == ["", "", "", "", ""]

    # Add the OUT action
    ner1.moves.add_action(5, "")
    ner1.add_label("GPE")
    # Get into the state just before "New"
    state1 = ner1.moves.init_batch([doc1])[0]
    ner1.moves.apply_transition(state1, "O")
    ner1.moves.apply_transition(state1, "O")
    ner1.moves.apply_transition(state1, "O")
    # Check that B-GPE is valid.
    assert ner1.moves.is_valid(state1, "B-GPE")

    # 2. test blocking behaviour
    nlp2 = English()
    doc2 = nlp2("I live in New York")
    ner2 = EntityRecognizer(doc2.vocab)

    # set "New" to a blocked entity
    doc2.ents = [(0, 3, 4)]
    assert [token.ent_iob_ for token in doc2] == ["", "", "", "B", ""]
    assert [token.ent_type_ for token in doc2] == ["", "", "", "", ""]

    # Check that B-GPE is now invalid.
    ner2.moves.add_action(5, "")
    ner2.add_label("GPE")
    state2 = ner2.moves.init_batch([doc2])[0]
    ner2.moves.apply_transition(state2, "O")
    ner2.moves.apply_transition(state2, "O")
    ner2.moves.apply_transition(state2, "O")
    assert not ner2.moves.is_valid(state2, "B-GPE")


def test_overwrite_token():
    nlp = English()
    ner1 = nlp.create_pipe("ner")
    nlp.add_pipe(ner1, name="ner")
    nlp.begin_training()

    # The untrained NER will predict O for each token
    doc = nlp("I live in New York")
    assert [token.ent_iob_ for token in doc] == ["O", "O", "O", "O", "O"]
    assert [token.ent_type_ for token in doc] == ["", "", "", "", ""]

    # Check that a new ner can overwrite O
    ner2 = EntityRecognizer(doc.vocab)
    ner2.moves.add_action(5, "")
    ner2.add_label("GPE")
    state = ner2.moves.init_batch([doc])[0]
    assert ner2.moves.is_valid(state, "B-GPE")
    assert ner2.moves.is_valid(state, "U-GPE")
    ner2.moves.apply_transition(state, "B-GPE")
    assert ner2.moves.is_valid(state, "I-GPE")
    assert ner2.moves.is_valid(state, "L-GPE")
