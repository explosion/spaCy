# coding: utf8
from __future__ import unicode_literals

import spacy

from spacy.lang.en import English
from spacy.pipeline import EntityRuler
from spacy.tokens import Span


def test_issue4267():
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


def test_todel_multiple_ner():
    nlp = English()

    # 1: untrained NER - should set everything to O
    # untrained_ner = nlp.create_pipe("ner")
    # untrained_ner.add_label("PEOPLE")
    # nlp.add_pipe(untrained_ner, name="uner")
    # nlp.begin_training()

    # 2 : Entity Ruler - should set "this" to B
    # ruler = EntityRuler(nlp)
    # patterns = [{"label": "thing", "pattern": "this"}]
    # ruler.add_patterns(patterns)
    # nlp.add_pipe(ruler)

    # 3 : trained NER - should set "Sofie" to B-PERSON and "Belgium" to B-GPE
    trained_ner = spacy.load("en_core_web_lg").get_pipe("ner")
    nlp.add_pipe(trained_ner)

    doc = nlp("Hi, this is Sofie speaking in Belgium")

    print()
    for token in doc:
        print(token.text, token.ent_iob_, token.ent_type_)


def test_todel_block_ner():
    nlp = English()

    # 1: block Sofie from being a named entity
    nlp.add_pipe(BlockerComponent())

    # 2 : trained NER - should ignore "Sofie" and set "Belgium" to B-GPE
    trained_ner = spacy.load("en_core_web_lg").get_pipe("ner")
    nlp.add_pipe(trained_ner)

    doc = nlp("Hi, this is Sofie speaking in Belgium")
    print()
    for token in doc:
        print(token.text, token.ent_iob_, token.ent_type_)


def test_todel_preset_ner():
    nlp = English()

    # 1: preset Sofie as B-PEEPZ
    nlp.add_pipe(PresetComponent())

    # 2 : trained NER - should ignore "Sofie" and set "Belgium" to B-GPE
    trained_ner = spacy.load("en_core_web_lg").get_pipe("ner")
    nlp.add_pipe(trained_ner)

    doc = nlp("Hi, this is Sofie speaking in Belgium")
    print()
    for token in doc:
        print(token.text, token.ent_iob_, token.ent_type_)


class BlockerComponent(object):
    name = "my_blocker"

    def __call__(self, doc):
        print("before", doc[4].text, doc[4].ent_iob_)
        # doc.ents = [(0, 4, 5)]            # OPTION 1: set type to 0 explicitly
        doc.ents = [Span(doc, 4, 5)]        # OPTION 2: implicit empty label
        print("after", doc[4].text, doc[4].ent_iob_)
        return doc


class PresetComponent(object):
    name = "my_presetter"

    def __call__(self, doc):
        print("before", doc[4].text, doc[4].ent_iob_)
        peepz = doc.vocab.strings.add("PEEPZ")
        print(peepz)
        doc.ents = [(peepz, 4, 5)]
        print("after", doc[4].text, doc[4].ent_iob_)
        return doc
