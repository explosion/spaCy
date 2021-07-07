from spacy.pipeline.ner import DEFAULT_NER_MODEL
from spacy.training import Example
from spacy.pipeline import EntityRecognizer
from spacy.tokens import Span, Doc
from spacy import registry
import pytest


def _ner_example(ner):
    doc = Doc(
        ner.vocab,
        words=["Joe", "loves", "visiting", "London", "during", "the", "weekend"],
    )
    gold = {"entities": [(0, 3, "PERSON"), (19, 25, "LOC")]}
    return Example.from_dict(doc, gold)


def test_doc_add_entities_set_ents_iob(en_vocab):
    text = ["This", "is", "a", "lion"]
    doc = Doc(en_vocab, words=text)
    cfg = {"model": DEFAULT_NER_MODEL}
    model = registry.resolve(cfg, validate=True)["model"]
    ner = EntityRecognizer(en_vocab, model)
    ner.initialize(lambda: [_ner_example(ner)])
    ner(doc)

    doc.ents = [("ANIMAL", 3, 4)]
    assert [w.ent_iob_ for w in doc] == ["O", "O", "O", "B"]

    doc.ents = [("WORD", 0, 2)]
    assert [w.ent_iob_ for w in doc] == ["B", "I", "O", "O"]


def test_ents_reset(en_vocab):
    """Ensure that resetting doc.ents does not change anything"""
    text = ["This", "is", "a", "lion"]
    doc = Doc(en_vocab, words=text)
    cfg = {"model": DEFAULT_NER_MODEL}
    model = registry.resolve(cfg, validate=True)["model"]
    ner = EntityRecognizer(en_vocab, model)
    ner.initialize(lambda: [_ner_example(ner)])
    ner(doc)
    orig_iobs = [t.ent_iob_ for t in doc]
    doc.ents = list(doc.ents)
    assert [t.ent_iob_ for t in doc] == orig_iobs


def test_add_overlapping_entities(en_vocab):
    text = ["Louisiana", "Office", "of", "Conservation"]
    doc = Doc(en_vocab, words=text)
    entity = Span(doc, 0, 4, label=391)
    doc.ents = [entity]

    new_entity = Span(doc, 0, 1, label=392)
    with pytest.raises(ValueError):
        doc.ents = list(doc.ents) + [new_entity]
