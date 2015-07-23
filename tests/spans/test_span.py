from __future__ import unicode_literals

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
