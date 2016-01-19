from __future__ import unicode_literals

import pytest
import numpy
from spacy.attrs import HEAD


@pytest.mark.models
def test_space_attachment(EN):
    sentence = 'This is a test.\nTo ensure  spaces are attached well.'
    doc = EN(sentence)

    for sent in doc.sents:
        if len(sent) == 1:
            assert not sent[-1].is_space


def test_sentence_space(EN):
    text = ('''I look forward to using Thingamajig.  I've been told it will '''
            '''make my life easier...''')
    doc = EN(text)
    assert len(list(doc.sents)) == 2

