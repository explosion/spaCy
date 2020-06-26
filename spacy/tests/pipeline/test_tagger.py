# coding: utf8
from __future__ import unicode_literals

import pytest
from spacy.language import Language
from spacy.symbols import POS, NOUN


def test_label_types():
    nlp = Language()
    nlp.add_pipe(nlp.create_pipe("tagger"))
    nlp.get_pipe("tagger").add_label("A")
    with pytest.raises(ValueError):
        nlp.get_pipe("tagger").add_label(9)


def test_tagger_begin_training_tag_map():
    """Test that Tagger.begin_training() without gold tuples does not clobber
    the tag map."""
    nlp = Language()
    tagger = nlp.create_pipe("tagger")
    orig_tag_count = len(tagger.labels)
    tagger.add_label("A", {"POS": "NOUN"})
    nlp.add_pipe(tagger)
    nlp.begin_training()
    assert nlp.vocab.morphology.tag_map["A"] == {POS: NOUN}
    assert orig_tag_count + 1 == len(nlp.get_pipe("tagger").labels)
