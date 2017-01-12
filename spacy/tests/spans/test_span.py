# coding: utf-8
from __future__ import unicode_literals

from ..util import get_doc

import pytest


@pytest.fixture
def doc(en_tokenizer):
    text = "This is a sentence. This is another sentence. And a third."
    heads = [1, 0, 1, -2, -3, 1, 0, 1, -2, -3, 0, 1, -2, -1]
    deps = ['nsubj', 'ROOT', 'det', 'attr', 'punct', 'nsubj', 'ROOT', 'det',
            'attr', 'punct', 'ROOT', 'det', 'npadvmod', 'punct']
    tokens = en_tokenizer(text)
    return get_doc(tokens.vocab, [t.text for t in tokens], heads=heads, deps=deps)


def test_spans_sent_spans(doc):
    sents = list(doc.sents)
    assert sents[0].start == 0
    assert sents[0].end == 5
    assert len(sents) == 3
    assert sum(len(sent) for sent in sents) == len(doc)


def test_spans_root(doc):
    span = doc[2:4]
    assert len(span) == 2
    assert span.text == 'a sentence'
    assert span.root.text == 'sentence'
    assert span.root.head.text == 'is'


def test_spans_root2(en_tokenizer):
    text = "through North and South Carolina"
    heads = [0, 3, -1, -2, -4]
    tokens = en_tokenizer(text)
    doc = get_doc(tokens.vocab, [t.text for t in tokens], heads=heads)
    assert doc[-2:].root.text == 'Carolina'


def test_spans_span_sent(doc):
    """Test span.sent property"""
    assert len(list(doc.sents))
    assert doc[:2].sent.root.text == 'is'
    assert doc[:2].sent.text == 'This is a sentence .'
    assert doc[6:7].sent.root.left_edge.text == 'This'


def test_spans_default_sentiment(en_tokenizer):
    """Test span.sentiment property's default averaging behaviour"""
    text = "good stuff bad stuff"
    tokens = en_tokenizer(text)
    tokens.vocab[tokens[0].text].sentiment = 3.0
    tokens.vocab[tokens[2].text].sentiment = -2.0
    doc = get_doc(tokens.vocab, [t.text for t in tokens])
    assert doc[:2].sentiment == 3.0 / 2
    assert doc[-2:].sentiment == -2. / 2
    assert doc[:-1].sentiment == (3.+-2) / 3.


def test_spans_override_sentiment(en_tokenizer):
    """Test span.sentiment property's default averaging behaviour"""
    text = "good stuff bad stuff"
    tokens = en_tokenizer(text)
    tokens.vocab[tokens[0].text].sentiment = 3.0
    tokens.vocab[tokens[2].text].sentiment = -2.0
    doc = get_doc(tokens.vocab, [t.text for t in tokens])
    doc.user_span_hooks['sentiment'] = lambda span: 10.0
    assert doc[:2].sentiment == 10.0
    assert doc[-2:].sentiment == 10.0
    assert doc[:-1].sentiment == 10.0
