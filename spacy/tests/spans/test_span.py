from __future__ import unicode_literals
from spacy.attrs import HEAD
from spacy.en import English
import numpy as np

import pytest


@pytest.fixture
def doc(EN):
    return EN('This is a sentence. This is another sentence. And a third.')


@pytest.mark.models
def test_sent_spans(doc):
    sents = list(doc.sents)
    assert sents[0].start == 0
    assert sents[0].end == 5
    assert len(sents) == 3
    assert sum(len(sent) for sent in sents) == len(doc)


@pytest.mark.models
def test_root(doc):
    np = doc[2:4]
    assert len(np) == 2
    assert np.orth_ == 'a sentence'
    assert np.root.orth_ == 'sentence'
    assert np.root.head.orth_ == 'is'


def test_root2():
    text = 'through North and South Carolina'
    EN = English(parser=False)
    doc = EN(text)
    heads = np.asarray([[0, 3, -1, -2, -4]], dtype='int32')
    doc.from_array([HEAD], heads.T)
    south_carolina = doc[-2:]
    assert south_carolina.root.text == 'Carolina'
