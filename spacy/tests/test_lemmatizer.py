# coding: utf8
from __future__ import unicode_literals

import pytest
from spacy.lang.en import English
from spacy.lookups import Lookups


def test_tagger_warns_no_lemma_lookups():
    nlp = English()
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
