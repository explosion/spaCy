from __future__ import unicode_literals

import pytest


@pytest.mark.xfail
@pytest.mark.models('en')
def test_issue758(EN):
    '''Test parser transition bug after label added.'''
    from ...matcher import merge_phrase
    nlp = EN()
    nlp.matcher.add('splash', merge_phrase, [[{'LEMMA': 'splash'}, {'LEMMA': 'on'}]])
    doc = nlp('splash On', parse=False)
