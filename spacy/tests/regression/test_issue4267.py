# coding: utf8
from __future__ import unicode_literals

import pytest

import spacy

from spacy.lang.en import English
from spacy.pipeline import EntityRuler
from spacy.tokens import Span


def test_issue4267():
    """ Test that running an entity_ruler after ner gives consistent results"""
    nlp = English()
    ner = nlp.create_pipe("ner")
    ner.add_label("PEOPLE")
    nlp.add_pipe(ner)
    nlp.begin_training()

    assert "ner" in nlp.pipe_names

    # assert that we have correct IOB annotations
    doc1 = nlp("hi")
    assert doc1.is_nered
    for token in doc1:
        assert token.ent_iob == 2

    # add entity ruler and run again
    ruler = EntityRuler(nlp)
    patterns = [{"label": "SOFTWARE", "pattern": "spacy"}]

    ruler.add_patterns(patterns)
    nlp.add_pipe(ruler)
    assert "entity_ruler" in nlp.pipe_names
    assert "ner" in nlp.pipe_names

    # assert that we still have correct IOB annotations
    doc2 = nlp("hi")
    assert doc2.is_nered
    for token in doc2:
        assert token.ent_iob == 2


def test_multiple_ner():
    """ Test that 2 NERs can work in sequence: the second can overwrite O annotations """
    nlp = English()

    # 1: untrained NER - should set everything to O
    untrained_ner = nlp.create_pipe("ner")
    untrained_ner.add_label("SMURFS")
    nlp.add_pipe(untrained_ner, name="uner")
    nlp.begin_training()

    # 2 : trained NER - should set "Antti L Korhonen" to PERSON and "Finland" to GPE
    # TODO: can't really use as unit test, using statistical model
    trained_ner = spacy.load("en_core_web_lg").get_pipe("ner")
    nlp.add_pipe(trained_ner)

    doc = nlp("This is Antti L Korhonen speaking in Finland")
    expected_iobs = ["O", "O", "B", "I", "I", "O", "O", "B"]
    expected_types = ["", "", "PERSON", "PERSON", "PERSON", "", "", "GPE"]
    assert [token.ent_iob_ for token in doc] == expected_iobs
    assert [token.ent_type_ for token in doc] == expected_types


def test_multiple_ner_2():
    """ Test that 2 NERs can work in sequence: the second respects the first annotations """
    nlp = English()

    # 2: untrained NER - should keep everything as is
    untrained_ner = nlp.create_pipe("ner")
    untrained_ner.add_label("SMURFS")
    # untrained_ner.add_label("PERSON")
    # untrained_ner.add_label("GPE")
    nlp.add_pipe(untrained_ner, name="uner")
    nlp.begin_training()

    # 1 : trained NER - should set "Antti Korhonen" to PERSON and "Finland" to GPE
    # TODO: can't really use as unit test, using statistical model
    trained_ner = spacy.load("en_core_web_lg").get_pipe("ner")
    nlp.add_pipe(trained_ner, before="uner")

    doc = nlp("This is Antti Korhonen speaking in Finland")

    # Because the untrained NER can do whatever it wants, we can't make assumptions on the other tokens
    assert doc[2].ent_iob_ == "B"
    assert doc[2].ent_type_ == "PERSON"
    assert doc[3].ent_iob_ == "I"
    assert doc[3].ent_type_ == "PERSON"
    assert doc[6].ent_iob_ == "B"
    assert doc[6].ent_type_ == "GPE"


def test_ruler_before_ner():
    """ Test that an NER works after an entity_ruler: the second can add annotations """
    nlp = English()

    # 1 : Entity Ruler - should set "this" to B and everything else to empty
    ruler = EntityRuler(nlp)
    patterns = [{"label": "THING", "pattern": "This"}]
    ruler.add_patterns(patterns)
    nlp.add_pipe(ruler)

    # 2: untrained NER - should set everything to O
    untrained_ner = nlp.create_pipe("ner")
    untrained_ner.add_label("SMURFS")
    nlp.add_pipe(untrained_ner)
    nlp.begin_training()

    doc = nlp("This is Antti Korhonen speaking in Finland")
    expected_iobs = ["B", "O", "O", "O", "O", "O", "O"]
    expected_types = ["THING", "", "", "", "", "", ""]
    assert [token.ent_iob_ for token in doc] == expected_iobs
    assert [token.ent_type_ for token in doc] == expected_types


def test_ner_before_ruler():
    """ Test that an entity_ruler works after an NER: the second can overwrite O annotations """
    nlp = English()

    # 1: untrained NER - should set everything to O
    untrained_ner = nlp.create_pipe("ner")
    untrained_ner.add_label("SMURFS")
    nlp.add_pipe(untrained_ner, name="uner")
    nlp.begin_training()

    # 2 : Entity Ruler - should set "this" to B and keep everything else O
    ruler = EntityRuler(nlp)
    patterns = [{"label": "THING", "pattern": "This"}]
    ruler.add_patterns(patterns)
    nlp.add_pipe(ruler)

    doc = nlp("This is Antti Korhonen speaking in Finland")
    expected_iobs = ["B", "O", "O", "O", "O", "O", "O"]
    expected_types = ["THING", "", "", "", "", "", ""]
    assert [token.ent_iob_ for token in doc] == expected_iobs
    assert [token.ent_type_ for token in doc] == expected_types


def test_block_ner():
    """ Test functionality for blocking tokens so they can't be in a named entity """

    # block "Antti" from being a named entity
    nlp = English()
    nlp.add_pipe(BlockerComponent1(2, 3))
    untrained_ner = nlp.create_pipe("ner")
    untrained_ner.add_label("SMURFS")
    nlp.add_pipe(untrained_ner, name="uner")
    nlp.begin_training()
    doc = nlp("This is Antti speaking in Finland")
    expected_iobs = ["O", "O", "B", "O", "O", "O"]
    expected_types = ["", "", "", "", "", ""]
    assert [token.ent_iob_ for token in doc] == expected_iobs
    assert [token.ent_type_ for token in doc] == expected_types

    # block "Antti Korhonen" from being a named entity
    nlp = English()
    nlp.add_pipe(BlockerComponent1(2, 4))
    untrained_ner = nlp.create_pipe("ner")
    untrained_ner.add_label("SMURFS")
    nlp.add_pipe(untrained_ner, name="uner")
    nlp.begin_training()
    doc = nlp("This is Antti Korhonen speaking in Finland")
    expected_iobs = ["O", "O", "B", "B", "O", "O", "O"]
    expected_types = ["", "", "", "", "", "", ""]
    assert [token.ent_iob_ for token in doc] == expected_iobs
    assert [token.ent_type_ for token in doc] == expected_types

    # block "Antti L Korhonen" from being a named entity
    nlp = English()
    nlp.add_pipe(BlockerComponent1(2, 5))
    untrained_ner = nlp.create_pipe("ner")
    untrained_ner.add_label("SMURFS")
    nlp.add_pipe(untrained_ner, name="uner")
    nlp.begin_training()
    doc = nlp("This is Antti L Korhonen speaking in Finland")
    expected_iobs = ["O", "O", "B", "B", "B", "O", "O", "O"]
    expected_types = ["", "", "", "", "", "", "", ""]
    assert [token.ent_iob_ for token in doc] == expected_iobs
    assert [token.ent_type_ for token in doc] == expected_types


def test_preset_ner_1():
    """ Test that an NER will respect pre-set tokens (single-token entity) """
    nlp = English()

    # 1: preset "Antti" as PEEPZ
    nlp.add_pipe(PresetComponent(2, 3))

    # 2 : trained NER - should ignore "Antti" and set "Finland" to GPE
    # TODO: can't really use as unit test, using statistical model
    trained_ner = spacy.load("en_core_web_lg").get_pipe("ner")
    nlp.add_pipe(trained_ner)

    doc = nlp("This is Antti speaking in Finland")

    expected_iobs = ["O", "O", "B", "O", "O", "B"]
    expected_types = ["", "", "PEEPZ", "", "", "GPE"]
    assert [token.ent_iob_ for token in doc] == expected_iobs
    assert [token.ent_type_ for token in doc] == expected_types


def test_preset_ner_2():
    """ Test that an NER will respect pre-set tokens (multiple-token entity) """
    nlp = English()

    # 1: preset "Antti Korhonen" as PEEPZ
    nlp.add_pipe(PresetComponent(2, 4))

    # 2 : trained NER - should ignore "Antti Korhonen" and set "Finland" to GPE
    # TODO: can't really use as unit test, using statistical model
    trained_ner = spacy.load("en_core_web_lg").get_pipe("ner")
    nlp.add_pipe(trained_ner)

    doc = nlp("This is Antti Korhonen speaking in Finland")

    expected_iobs = ["O", "O", "B", "I", "O", "O", "B"]
    expected_types = ["", "", "PEEPZ", "PEEPZ", "", "", "GPE"]
    assert [token.ent_iob_ for token in doc] == expected_iobs
    assert [token.ent_type_ for token in doc] == expected_types


def test_preset_ner_3():
    """ Test that an NER will respect pre-set tokens (multiple-token entity) """
    nlp = English()

    # 1: preset "Antti L Korhonen" as PEEPZ
    nlp.add_pipe(PresetComponent(2, 5))

    # 2 : trained NER - should ignore "Antti Korhonen" and set "Finland" to GPE
    # TODO: can't really use as unit test, using statistical model
    trained_ner = spacy.load("en_core_web_lg").get_pipe("ner")
    nlp.add_pipe(trained_ner)

    doc = nlp("This is Antti L Korhonen speaking in Finland")

    expected_iobs = ["O", "O", "B", "I", "I", "O", "O", "B"]
    expected_types = ["", "", "PEEPZ", "PEEPZ", "PEEPZ", "", "", "GPE"]
    assert [token.ent_iob_ for token in doc] == expected_iobs
    assert [token.ent_type_ for token in doc] == expected_types


class BlockerComponent1(object):
    name = "my_blocker"

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __call__(self, doc):
        doc.ents = [(0, self.start, self.end)]
        return doc


class BlockerComponent2(object):
    name = "my_blocker"

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __call__(self, doc):
        doc.ents = [Span(doc, self.start, self.end)]
        return doc


class PresetComponent(object):
    name = "my_presetter"

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __call__(self, doc):
        peepz = doc.vocab.strings.add("PEEPZ")
        doc.ents = [(peepz, self.start, self.end)]
        return doc
