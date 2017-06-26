# coding: utf-8
from __future__ import unicode_literals

from ...matcher import Matcher

import pytest


pattern1 = [[{'LOWER': 'celtics'}], [{'LOWER': 'boston'}, {'LOWER': 'celtics'}]]
pattern2 = [[{'LOWER': 'boston'}, {'LOWER': 'celtics'}], [{'LOWER': 'celtics'}]]
pattern3 = [[{'LOWER': 'boston'}], [{'LOWER': 'boston'}, {'LOWER': 'celtics'}]]
pattern4 = [[{'LOWER': 'boston'}, {'LOWER': 'celtics'}], [{'LOWER': 'boston'}]]


@pytest.fixture
def doc(en_tokenizer):
    text = "how many points did lebron james score against the boston celtics last night"
    doc = en_tokenizer(text)
    return doc


@pytest.mark.parametrize('pattern', [pattern1, pattern2])
def test_issue118(doc, pattern):
    """Test a bug that arose from having overlapping matches"""
    ORG = doc.vocab.strings['ORG']
    matcher = Matcher(doc.vocab)
    matcher.add("BostonCeltics", None, *pattern)

    assert len(list(doc.ents)) == 0
    matches = [(ORG, start, end) for _, start, end in matcher(doc)]
    assert matches == [(ORG, 9, 11), (ORG, 10, 11)]
    doc.ents = matches[:1]
    ents = list(doc.ents)
    assert len(ents) == 1
    assert ents[0].label == ORG
    assert ents[0].start == 9
    assert ents[0].end == 11


@pytest.mark.parametrize('pattern', [pattern3, pattern4])
def test_issue118_prefix_reorder(doc, pattern):
    """Test a bug that arose from having overlapping matches"""
    ORG = doc.vocab.strings['ORG']
    matcher = Matcher(doc.vocab)
    matcher.add('BostonCeltics', None, *pattern)

    assert len(list(doc.ents)) == 0
    matches = [(ORG, start, end) for _, start, end in matcher(doc)]
    doc.ents += tuple(matches)[1:]
    assert matches == [(ORG, 9, 10), (ORG, 9, 11)]
    ents = doc.ents
    assert len(ents) == 1
    assert ents[0].label == ORG
    assert ents[0].start == 9
    assert ents[0].end == 11
