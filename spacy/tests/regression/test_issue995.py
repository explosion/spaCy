from __future__ import unicode_literals

import pytest
from ... import load as load_spacy

@pytest.fixture
def doc():
    nlp = load_spacy('en')
    return nlp('Does flight number three fifty-four require a connecting flight'
               ' to get to Boston?')


@pytest.mark.models
def test_issue955(doc):
    '''Test that we don't have any nested noun chunks'''
    seen_tokens = set()
    for np in doc.noun_chunks:
        print(np.text, np.root.text, np.root.dep_, np.root.tag_)
        for word in np:
            key = (word.i, word.text)
            assert key not in seen_tokens
            seen_tokens.add(key)
