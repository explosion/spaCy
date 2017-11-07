import pytest
import spacy

@pytest.mark.models('en')
def test_issue1305():
    '''Test lemmatization of English VBZ'''
    nlp = spacy.load('en_core_web_sm')
    assert nlp.vocab.morphology.lemmatizer('works', 'verb') == ['work']
    doc = nlp(u'This app works well')
    assert doc[2].lemma_ == 'work'
