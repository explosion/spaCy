from __future__ import unicode_literals
from spacy.attrs import HEAD
from spacy.en import English
from spacy.tokens.doc import Doc
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


def test_root2(EN):
    text = 'through North and South Carolina'
    doc = EN(text)
    heads = np.asarray([[0, 3, -1, -2, -4]], dtype='int32')
    doc.from_array([HEAD], heads.T)
    south_carolina = doc[-2:]
    assert south_carolina.root.text == 'Carolina'


def test_sent(doc):
    '''Test new span.sent property'''
    #return EN('This is a sentence. This is another sentence. And a third.')
    heads = np.asarray([[1, 0, -1, -1, -1, 1, 0, -1, -1, -1, 2, 1, 0, -1]], dtype='int32')
    doc.from_array([HEAD], heads.T)
    assert len(list(doc.sents))
    span = doc[:2]
    assert span.sent.root.text == 'is'
    assert span.sent.text == 'This is a sentence.'
    span = doc[6:7]
    assert span.sent.root.left_edge.text == 'This'


def test_default_sentiment(EN):
    '''Test new span.sentiment property's default averaging behaviour'''
    good = EN.vocab[u'good']
    good.sentiment = 3.0
    bad = EN.vocab[u'bad']
    bad.sentiment = -2.0

    doc = Doc(EN.vocab, [u'good', 'stuff', u'bad', u'stuff'])

    good_stuff = doc[:2]
    assert good_stuff.sentiment == 3.0 / 2

    bad_stuff = doc[-2:]
    assert bad_stuff.sentiment == -2. / 2

    good_stuff_bad = doc[:-1]
    assert good_stuff_bad.sentiment == (3.+-2) / 3.



def test_override_sentiment(EN):
    '''Test new span.sentiment property's default averaging behaviour'''
    good = EN.vocab[u'good']
    good.sentiment = 3.0
    bad = EN.vocab[u'bad']
    bad.sentiment = -2.0

    doc = Doc(EN.vocab, [u'good', 'stuff', u'bad', u'stuff'])

    doc.user_span_hooks['sentiment'] = lambda span: 10.0

    good_stuff = doc[:2]
    assert good_stuff.sentiment == 10.0

    bad_stuff = doc[-2:]
    assert bad_stuff.sentiment == 10.0

    good_stuff_bad = doc[:-1]
    assert good_stuff_bad.sentiment == 10.0
