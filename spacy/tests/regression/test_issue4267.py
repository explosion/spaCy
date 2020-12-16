# coding: utf8
from __future__ import unicode_literals

from spacy.lang.en import English
from spacy.pipeline import EntityRuler


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
