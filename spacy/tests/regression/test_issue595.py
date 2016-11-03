import pytest

import spacy


@pytest.mark.models
def test_not_lemmatize_base_forms():
    nlp = spacy.load('en', parser=False)
    doc = nlp(u"Don't feed the dog")
    feed = doc[2]
    feed.tag_ = u'VB'
    assert feed.text == u'feed'
    assert feed.lemma_ == u'feed'

