from __future__ import unicode_literals
from ... import load as load_spacy
from ...attrs import LEMMA
from ...matcher import merge_phrase

import pytest


@pytest.mark.models
def test_issue758():
    '''Test parser transition bug after label added.'''
    nlp = load_spacy('en')
    nlp.matcher.add('splash', 'my_entity', {},
                    [[{LEMMA: 'splash'}, {LEMMA: 'on'}]],
                    on_match=merge_phrase)
    doc = nlp('splash On', parse=False)
