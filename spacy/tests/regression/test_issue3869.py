# coding: utf8
from __future__ import unicode_literals

import pytest

from spacy.attrs import IS_ALPHA
from spacy.lang.en import English


@pytest.mark.parametrize(
    "sentence",
    [
        'The story was to the effect that a young American student recently called on Professor Christlieb with a letter of introduction.',
        'The next month Barry Siddall joined Stoke City on a free transfer, after Chris Pearce had established himself as the Vale\'s #1.'
    ],
)
def test_issue3869(sentence):
    """Test that the Doc's count_by function works consistently"""
    nlp = English()

    doc = nlp(sentence)

    count = 0
    for token in doc:
        count += token.is_alpha

    assert count == doc.count_by(IS_ALPHA).get(1, 0)


