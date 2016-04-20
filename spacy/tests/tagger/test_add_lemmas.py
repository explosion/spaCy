from __future__ import unicode_literals

from spacy.en import English
import pytest

@pytest.mark.models
def test_lemma_assignment(EN):
    tokens = u'Bananas in pyjamas are geese .'.split(' ')
    doc = EN.tokenizer.tokens_from_list(tokens)
    assert all( t.lemma_ == u'' for t in doc )
    EN.tagger(doc)
    assert all( t.lemma_ != u'' for t in doc )
