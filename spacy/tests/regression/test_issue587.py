import spacy
import spacy.matcher
from spacy.attrs import IS_PUNCT, ORTH

import pytest

@pytest.mark.models
def test_matcher_segfault():
    nlp = spacy.load('en', parser=False, entity=False)
    matcher = spacy.matcher.Matcher(nlp.vocab)
    content = u'''a b; c'''
    matcher.add(entity_key='1', label='TEST', attrs={}, specs=[[{ORTH: 'a'}, {ORTH: 'b'}]])
    matcher(nlp(content))
    matcher.add(entity_key='2', label='TEST', attrs={}, specs=[[{ORTH: 'a'}, {ORTH: 'b'}, {IS_PUNCT: True}, {ORTH: 'c'}]])
    matcher(nlp(content))
    matcher.add(entity_key='3', label='TEST', attrs={}, specs=[[{ORTH: 'a'}, {ORTH: 'b'}, {IS_PUNCT: True}, {ORTH: 'd'}]])
    matcher(nlp(content))
