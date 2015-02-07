from __future__ import unicode_literals
from spacy.en import English

import pytest

@pytest.fixture
def tokens():
    nlp = English()
    return nlp(u'Give it back! He pleaded.')


def test_getitem(tokens):
    assert tokens[0].orth_ == 'Give'
    assert tokens[-1].orth_ == '.'
    with pytest.raises(IndexError):
        tokens[len(tokens)]
