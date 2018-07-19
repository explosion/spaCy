# coding: utf-8
from __future__ import unicode_literals

import pytest
from spacy.matcher import Matcher, PhraseMatcher
from spacy.tokens import Doc


@pytest.fixture
def matcher(en_vocab):
    rules = {'JS':        [[{'ORTH': 'JavaScript'}]],
             'GoogleNow': [[{'ORTH': 'Google'}, {'ORTH': 'Now'}]],
             'Java':      [[{'LOWER': 'java'}]]}
    matcher = Matcher(en_vocab)
    for key, patterns in rules.items():
        matcher.add(key, None, *patterns)
    return matcher


def test_matcher_from_api_docs(en_vocab):
    matcher = Matcher(en_vocab)
    pattern = [{'ORTH': 'test'}]
    assert len(matcher) == 0
    matcher.add('Rule', None, pattern)
    assert len(matcher) == 1
    matcher.remove('Rule')
    assert 'Rule' not in matcher
    matcher.add('Rule', None, pattern)
    assert 'Rule' in matcher
    on_match, patterns = matcher.get('Rule')
    assert len(patterns[0])


def test_matcher_from_usage_docs(en_vocab):
    text = "Wow 😀 This is really cool! 😂 😂"
    doc = Doc(en_vocab, words=text.split(' '))
    pos_emoji = ['😀', '😃', '😂', '🤣', '😊', '😍']
    pos_patterns = [[{'ORTH': emoji}] for emoji in pos_emoji]

    def label_sentiment(matcher, doc, i, matches):
        match_id, start, end = matches[i]
        if doc.vocab.strings[match_id] == 'HAPPY':
            doc.sentiment += 0.1
        span = doc[start : end]
        token = span.merge()
        token.vocab[token.text].norm_ = 'happy emoji'

    matcher = Matcher(en_vocab)
    matcher.add('HAPPY', label_sentiment, *pos_patterns)
    matches = matcher(doc)
    assert doc.sentiment != 0
    assert doc[1].norm_ == 'happy emoji'


@pytest.mark.parametrize('words', [["Some", "words"]])
def test_matcher_init(en_vocab, words):
    matcher = Matcher(en_vocab)
    doc = Doc(en_vocab, words=words)
    assert len(matcher) == 0
    assert matcher(doc) == []


def test_matcher_contains(matcher):
    matcher.add('TEST', None, [{'ORTH': 'test'}])
    assert 'TEST' in matcher
    assert 'TEST2' not in matcher


def test_matcher_no_match(matcher):
    words = ["I", "like", "cheese", "."]
    doc = Doc(matcher.vocab, words=words)
    assert matcher(doc) == []


def test_matcher_compile(matcher):
    assert len(matcher) == 3


def test_matcher_match_start(matcher):
    words = ["JavaScript", "is", "good"]
    doc = Doc(matcher.vocab, words=words)
    assert matcher(doc) == [(matcher.vocab.strings['JS'], 0, 1)]


def test_matcher_match_end(matcher):
    words = ["I", "like", "java"]
    doc = Doc(matcher.vocab, words=words)
    assert matcher(doc) == [(doc.vocab.strings['Java'], 2, 3)]


def test_matcher_match_middle(matcher):
    words = ["I", "like", "Google", "Now", "best"]
    doc = Doc(matcher.vocab, words=words)
    assert matcher(doc) == [(doc.vocab.strings['GoogleNow'], 2, 4)]


def test_matcher_match_multi(matcher):
    words = ["I", "like", "Google", "Now", "and", "java", "best"]
    doc = Doc(matcher.vocab, words=words)
    assert matcher(doc) == [(doc.vocab.strings['GoogleNow'], 2, 4),
                            (doc.vocab.strings['Java'], 5, 6)]
