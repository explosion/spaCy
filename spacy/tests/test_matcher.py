# coding: utf-8
from __future__ import unicode_literals

from ..matcher import Matcher, PhraseMatcher
from .util import get_doc

import pytest


@pytest.fixture
def matcher(en_vocab):
    rules = {
        'JS':        [[{'ORTH': 'JavaScript'}]],
        'GoogleNow': [[{'ORTH': 'Google'}, {'ORTH': 'Now'}]],
        'Java':      [[{'LOWER': 'java'}]]
    }
    matcher = Matcher(en_vocab)
    for key, patterns in rules.items():
        matcher.add(key, None, *patterns)
    return matcher


@pytest.mark.parametrize('words', [["Some", "words"]])
def test_matcher_init(en_vocab, words):
    matcher = Matcher(en_vocab)
    doc = get_doc(en_vocab, words)
    assert len(matcher) == 0
    assert matcher(doc) == []


def test_matcher_no_match(matcher):
    words = ["I", "like", "cheese", "."]
    doc = get_doc(matcher.vocab, words)
    assert matcher(doc) == []


def test_matcher_compile(matcher):
    assert len(matcher) == 3


def test_matcher_match_start(matcher):
    words = ["JavaScript", "is", "good"]
    doc = get_doc(matcher.vocab, words)
    assert matcher(doc) == [(matcher.vocab.strings['JS'], 0, 1)]


def test_matcher_match_end(matcher):
    words = ["I", "like", "java"]
    doc = get_doc(matcher.vocab, words)
    assert matcher(doc) == [(doc.vocab.strings['Java'], 2, 3)]


def test_matcher_match_middle(matcher):
    words = ["I", "like", "Google", "Now", "best"]
    doc = get_doc(matcher.vocab, words)
    assert matcher(doc) == [(doc.vocab.strings['GoogleNow'], 2, 4)]


def test_matcher_match_multi(matcher):
    words = ["I", "like", "Google", "Now", "and", "java", "best"]
    doc = get_doc(matcher.vocab, words)
    assert matcher(doc) == [(doc.vocab.strings['GoogleNow'], 2, 4),
                            (doc.vocab.strings['Java'], 5, 6)]


@pytest.mark.xfail
def test_matcher_phrase_matcher(en_vocab):
    words = ["Google", "Now"]
    doc = get_doc(en_vocab, words)
    matcher = PhraseMatcher(en_vocab, [doc])
    words = ["I", "like", "Google", "Now", "best"]
    doc = get_doc(en_vocab, words)
    assert len(matcher(doc)) == 1


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
    doc = get_doc(matcher.vocab, words1)
    assert len(matcher(doc)) == 1

    doc = get_doc(matcher.vocab, words2)
    assert len(matcher(doc)) == 0
    matcher.add('Quote', None, pattern2)
    assert len(matcher(doc)) == 0


def test_matcher_match_zero_plus(matcher):
    words = 'He said , " some words " ...'.split()
    pattern = [{'ORTH': '"'},
               {'OP': '*', 'IS_PUNCT': False},
               {'ORTH': '"'}]
    matcher.add('Quote', None, pattern)
    doc = get_doc(matcher.vocab, words)
    assert len(matcher(doc)) == 1


def test_matcher_match_one_plus(matcher):
    control = Matcher(matcher.vocab)
    control.add('BasicPhilippe', None, [{'ORTH': 'Philippe'}])
    doc = get_doc(control.vocab, ['Philippe', 'Philippe'])
    m = control(doc)
    assert len(m) == 2
    matcher.add('KleenePhilippe', None, [{'ORTH': 'Philippe', 'OP': '1'},
                                         {'ORTH': 'Philippe', 'OP': '+'}])
    m = matcher(doc)
    assert len(m) == 1
