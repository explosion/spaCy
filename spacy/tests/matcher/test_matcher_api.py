# coding: utf-8
from __future__ import unicode_literals

import pytest
from spacy.matcher import Matcher
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


def test_matcher_len_contains(matcher):
    assert len(matcher) == 3
    matcher.add('TEST', None, [{'ORTH': 'test'}])
    assert 'TEST' in matcher
    assert 'TEST2' not in matcher


def test_matcher_no_match(matcher):
    doc = Doc(matcher.vocab, words=["I", "like", "cheese", "."])
    assert matcher(doc) == []


def test_matcher_match_start(matcher):
    doc = Doc(matcher.vocab, words=["JavaScript", "is", "good"])
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


def test_matcher_empty_dict(en_vocab):
    """Test matcher allows empty token specs, meaning match on any token."""
    matcher = Matcher(en_vocab)
    doc = Doc(matcher.vocab, words=["a", "b", "c"])
    matcher.add('A.C', None, [{'ORTH': 'a'}, {}, {'ORTH': 'c'}])
    matches = matcher(doc)
    assert len(matches) == 1
    assert matches[0][1:] == (0, 3)
    matcher = Matcher(en_vocab)
    matcher.add('A.', None, [{'ORTH': 'a'}, {}])
    matches = matcher(doc)
    assert matches[0][1:] == (0, 2)


def test_matcher_operator_shadow(en_vocab):
    matcher = Matcher(en_vocab)
    doc = Doc(matcher.vocab, words=["a", "b", "c"])
    pattern = [{'ORTH': 'a'}, {"IS_ALPHA": True, "OP": "+"}, {'ORTH': 'c'}]
    matcher.add('A.C', None, pattern)
    matches = matcher(doc)
    assert len(matches) == 1
    assert matches[0][1:] == (0, 3)


def test_matcher_match_zero(matcher):
    words1 = 'He said , " some words " ...'.split()
    words2 = 'He said , " some three words " ...'.split()
    pattern1 = [{'ORTH': '"'},
                {'OP': '!', 'IS_PUNCT': True},
                {'OP': '!', 'IS_PUNCT': True},
                {'ORTH': '"'}]
    pattern2 = [{'ORTH': '"'},
                {'IS_PUNCT': True},
                {'IS_PUNCT': True},
                {'IS_PUNCT': True},
                {'ORTH': '"'}]
    matcher.add('Quote', None, pattern1)
    doc = Doc(matcher.vocab, words=words1)
    assert len(matcher(doc)) == 1
    doc = Doc(matcher.vocab, words=words2)
    assert len(matcher(doc)) == 0
    matcher.add('Quote', None, pattern2)
    assert len(matcher(doc)) == 0


def test_matcher_match_zero_plus(matcher):
    words = 'He said , " some words " ...'.split()
    pattern = [{'ORTH': '"'},
                {'OP': '*', 'IS_PUNCT': False},
                {'ORTH': '"'}]
    matcher = Matcher(matcher.vocab)
    matcher.add('Quote', None, pattern)
    doc = Doc(matcher.vocab, words=words)
    assert len(matcher(doc)) == 1


def test_matcher_match_one_plus(matcher):
    control = Matcher(matcher.vocab)
    control.add('BasicPhilippe', None, [{'ORTH': 'Philippe'}])
    doc = Doc(control.vocab, words=['Philippe', 'Philippe'])
    m = control(doc)
    assert len(m) == 2
    matcher.add('KleenePhilippe', None, [{'ORTH': 'Philippe', 'OP': '1'},
                                         {'ORTH': 'Philippe', 'OP': '+'}])
    m = matcher(doc)
    assert len(m) == 1


def test_matcher_any_token_operator(en_vocab):
    """Test that patterns with "any token" {} work with operators."""
    matcher = Matcher(en_vocab)
    matcher.add('TEST', None, [{'ORTH': 'test'}, {'OP': '*'}])
    doc = Doc(en_vocab, words=['test', 'hello', 'world'])
    matches = [doc[start:end].text for _, start, end in matcher(doc)]
    assert len(matches) == 3
    assert matches[0] == 'test'
    assert matches[1] == 'test hello'
    assert matches[2] == 'test hello world'
