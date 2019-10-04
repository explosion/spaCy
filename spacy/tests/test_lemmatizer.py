# coding: utf8
from __future__ import unicode_literals

import pytest
from spacy.tokens import Doc
from spacy.language import Language
from spacy.lookups import Lookups


def test_lemmatizer_reflects_lookups_changes():
    """Test for an issue that'd cause lookups available in a model loaded from
    disk to not be reflected in the lemmatizer."""
    nlp = Language()
    assert Doc(nlp.vocab, words=["foo"])[0].lemma_ == "foo"
    table = nlp.vocab.lookups.add_table("lemma_lookup")
    table["foo"] = "bar"
    assert Doc(nlp.vocab, words=["foo"])[0].lemma_ == "bar"
    table = nlp.vocab.lookups.get_table("lemma_lookup")
    table["hello"] = "world"
    # The update to the table should be reflected in the lemmatizer
    assert Doc(nlp.vocab, words=["hello"])[0].lemma_ == "world"
    new_nlp = Language()
    table = new_nlp.vocab.lookups.add_table("lemma_lookup")
    table["hello"] = "hi"
    assert Doc(new_nlp.vocab, words=["hello"])[0].lemma_ == "hi"
    nlp_bytes = nlp.to_bytes()
    new_nlp.from_bytes(nlp_bytes)
    # Make sure we have the previously saved lookup table
    assert len(new_nlp.vocab.lookups) == 1
    assert len(new_nlp.vocab.lookups.get_table("lemma_lookup")) == 2
    assert new_nlp.vocab.lookups.get_table("lemma_lookup")["hello"] == "world"
    assert Doc(new_nlp.vocab, words=["foo"])[0].lemma_ == "bar"
    assert Doc(new_nlp.vocab, words=["hello"])[0].lemma_ == "world"


def test_tagger_warns_no_lemma_lookups():
    nlp = Language()
    nlp.vocab.lookups = Lookups()
    assert not len(nlp.vocab.lookups)
    tagger = nlp.create_pipe("tagger")
    with pytest.warns(UserWarning):
        tagger.begin_training()
    nlp.add_pipe(tagger)
    with pytest.warns(UserWarning):
        nlp.begin_training()
    nlp.vocab.lookups.add_table("lemma_lookup")
    with pytest.warns(None) as record:
        nlp.begin_training()
        assert not record.list
