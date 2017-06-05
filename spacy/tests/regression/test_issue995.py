from __future__ import unicode_literals

import pytest


@pytest.mark.models('en')
def test_issue955(EN):
    '''Test that we don't have any nested noun chunks'''
    doc = EN('Does flight number three fifty-four require a connecting flight'
             ' to get to Boston?')
    seen_tokens = set()
    for np in doc.noun_chunks:
        for word in np:
            key = (word.i, word.text)
            assert key not in seen_tokens
            seen_tokens.add(key)
