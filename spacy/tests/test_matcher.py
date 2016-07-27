from __future__ import unicode_literals
import pytest

from spacy.strings import StringStore
from spacy.matcher import *
from spacy.attrs import LOWER
from spacy.tokens.doc import Doc
from spacy.vocab import Vocab


@pytest.fixture
def matcher(EN):
    patterns = {
        'Javascript': ['PRODUCT', {}, [[{'ORTH': 'JavaScript'}]]],
        'GoogleNow':  ['PRODUCT', {}, [[{'ORTH': 'Google'}, {'ORTH': 'Now'}]]],
        'Java':       ['PRODUCT', {}, [[{'LOWER': 'java'}]]],
    }
    return Matcher(EN.vocab, patterns)


def test_compile(matcher):
    assert matcher.n_patterns == 3


def test_no_match(matcher, EN):
    tokens = EN('I like cheese')
    assert matcher(tokens) == []


def test_match_start(matcher, EN):
    tokens = EN('JavaScript is good')
    assert matcher(tokens) == [(EN.vocab.strings['PRODUCT'], 0, 1)]


def test_match_end(matcher, EN):
    tokens = EN('I like java')
    assert matcher(tokens) == [(EN.vocab.strings['PRODUCT'], 2, 3)]


def test_match_middle(matcher, EN):
    tokens = EN('I like Google Now best')
    assert matcher(tokens) == [(EN.vocab.strings['PRODUCT'], 2, 4)]


def test_match_multi(matcher, EN):
    tokens = EN('I like Google Now and java best')
    assert matcher(tokens) == [(EN.vocab.strings['PRODUCT'], 2, 4),
                               (EN.vocab.strings['PRODUCT'], 5, 6)]


@pytest.mark.models
def test_match_preserved(matcher, EN):
    doc = EN.tokenizer('I like java')
    EN.tagger(doc)
    assert len(doc.ents) == 0
    doc = EN.tokenizer('I like java')
    matcher(doc)
    assert len(doc.ents) == 1
    EN.tagger(doc)
    EN.entity(doc)
    assert len(doc.ents) == 1
