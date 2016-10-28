import spacy
import spacy.matcher

import pytest

@pytest.mark.models
def test_matcher_segfault():
    nlp = spacy.load('en', parser=False, entity=False)
    matcher = spacy.matcher.Matcher(nlp.vocab)
    content = u'''a b; c'''
    matcher.add(entity_key='1', label='TEST', attrs={}, specs=[[{65: 'a'}, {65: 'b'}]])
    matcher(nlp(content))
    matcher.add(entity_key='2', label='TEST', attrs={}, specs=[[{65: 'a'}, {65: 'b'}, {5: True}, {65: 'c'}]])
    matcher(nlp(content))
    matcher.add(entity_key='3', label='TEST', attrs={}, specs=[[{65: 'a'}, {65: 'b'}, {5: True}, {65: 'd'}]])
    matcher(nlp(content))
