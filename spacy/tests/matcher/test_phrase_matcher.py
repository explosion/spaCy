# coding: utf-8
from __future__ import unicode_literals

import pytest
from spacy.matcher import PhraseMatcher
from spacy.tokens import Doc


def test_matcher_phrase_matcher(en_vocab):
    doc = Doc(en_vocab, words=["Google", "Now"])
    matcher = PhraseMatcher(en_vocab)
    matcher.add('COMPANY', None, doc)
    doc = Doc(en_vocab, words=["I", "like", "Google", "Now", "best"])
    assert len(matcher(doc)) == 1


def test_phrase_matcher_length(en_vocab):
    matcher = PhraseMatcher(en_vocab)
    assert len(matcher) == 0
    matcher.add('TEST', None, Doc(en_vocab, words=['test']))
    assert len(matcher) == 1
    matcher.add('TEST2', None, Doc(en_vocab, words=['test2']))
    assert len(matcher) == 2


def test_phrase_matcher_contains(en_vocab):
    matcher = PhraseMatcher(en_vocab)
    matcher.add('TEST', None, Doc(en_vocab, words=['test']))
    assert 'TEST' in matcher
    assert 'TEST2' not in matcher
