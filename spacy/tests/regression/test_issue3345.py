# coding: utf8
from __future__ import unicode_literals

from spacy.lang.en import English
from spacy.tokens import Doc
from spacy.pipeline import EntityRuler, EntityRecognizer


def test_issue3345():
    """Test case where preset entity crosses sentence boundary."""
    nlp = English()
    doc = Doc(nlp.vocab, words=["I", "live", "in", "New", "York"])
    doc[4].is_sent_start = True
    ruler = EntityRuler(nlp, patterns=[{"label": "GPE", "pattern": "New York"}])
    ner = EntityRecognizer(doc.vocab)
    # Add the OUT action. I wouldn't have thought this would be necessary...
    ner.moves.add_action(5, "")
    ner.add_label("GPE")
    doc = ruler(doc)
    # Get into the state just before "New"
    state = ner.moves.init_batch([doc])[0]
    ner.moves.apply_transition(state, "O")
    ner.moves.apply_transition(state, "O")
    ner.moves.apply_transition(state, "O")
    # Check that B-GPE is valid.
    assert ner.moves.is_valid(state, "B-GPE")
