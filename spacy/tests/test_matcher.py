# coding: utf-8
from __future__ import unicode_literals

from numpy import sort

from ..matcher import Matcher, PhraseMatcher, DependencyTreeMatcher
from .util import get_doc
from ..tokens import Doc

import pytest
import re

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
    doc = get_doc(en_vocab, words=text.split(' '))
    pos_emoji = [u'😀', u'😃', u'😂', u'🤣', u'😊', u'😍']
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
    doc = get_doc(en_vocab, words)
    assert len(matcher) == 0
    assert matcher(doc) == []


def test_matcher_contains(matcher):
    matcher.add('TEST', None, [{'ORTH': 'test'}])
    assert 'TEST' in matcher
    assert 'TEST2' not in matcher


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


def test_matcher_empty_dict(en_vocab):
    '''Test matcher allows empty token specs, meaning match on any token.'''
    matcher = Matcher(en_vocab)
    abc = ["a", "b", "c"]
    doc = get_doc(matcher.vocab, abc)
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
    abc = ["a", "b", "c"]
    doc = get_doc(matcher.vocab, abc)
    matcher.add('A.C', None, [{'ORTH': 'a'},
                              {"IS_ALPHA": True, "OP": "+"},
                              {'ORTH': 'c'}])
    matches = matcher(doc)
    assert len(matches) == 1
    assert matches[0][1:] == (0, 3)


def test_matcher_phrase_matcher(en_vocab):
    words = ["Google", "Now"]
    doc = get_doc(en_vocab, words)
    matcher = PhraseMatcher(en_vocab)
    matcher.add('COMPANY', None, doc)
    words = ["I", "like", "Google", "Now", "best"]
    doc = get_doc(en_vocab, words)
    assert len(matcher(doc)) == 1


def test_phrase_matcher_length(en_vocab):
    matcher = PhraseMatcher(en_vocab)
    assert len(matcher) == 0
    matcher.add('TEST', None, get_doc(en_vocab, ['test']))
    assert len(matcher) == 1
    matcher.add('TEST2', None, get_doc(en_vocab, ['test2']))
    assert len(matcher) == 2


def test_phrase_matcher_contains(en_vocab):
    matcher = PhraseMatcher(en_vocab)
    matcher.add('TEST', None, get_doc(en_vocab, ['test']))
    assert 'TEST' in matcher
    assert 'TEST2' not in matcher


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


def test_operator_combos(matcher):
    cases = [
        ('aaab', 'a a a b', True),
        ('aaab', 'a+ b', True),
        ('aaab', 'a+ a+ b', True),
        ('aaab', 'a+ a+ a b', True),
        ('aaab', 'a+ a+ a+ b', True),
        ('aaab', 'a+ a a b', True),
        ('aaab', 'a+ a a', True),
        ('aaab', 'a+', True),
        ('aaa', 'a+ b', False),
        ('aaa', 'a+ a+ b', False),
        ('aaa', 'a+ a+ a+ b', False),
        ('aaa', 'a+ a b', False),
        ('aaa', 'a+ a a b', False),
        ('aaab', 'a+ a a', True),
        ('aaab', 'a+', True),
        ('aaab', 'a+ a b', True),
    ]
    for string, pattern_str, result in cases:
        matcher = Matcher(matcher.vocab)
        doc = get_doc(matcher.vocab, words=list(string))
        pattern = []
        for part in pattern_str.split():
            if part.endswith('+'):
                pattern.append({'ORTH': part[0], 'op': '+'})
            else:
                pattern.append({'ORTH': part})
        matcher.add('PATTERN', None, pattern)
        matches = matcher(doc)
        if result:
            assert matches, (string, pattern_str)
        else:
            assert not matches, (string, pattern_str)


def test_matcher_end_zero_plus(matcher):
    '''Test matcher works when patterns end with * operator. (issue 1450)'''
    matcher = Matcher(matcher.vocab)
    matcher.add(
        "TSTEND",
        None,
        [
            {'ORTH': "a"},
            {'ORTH': "b", 'OP': "*"}
        ]
    )
    nlp = lambda string: Doc(matcher.vocab, words=string.split())
    assert len(matcher(nlp(u'a'))) == 1
    assert len(matcher(nlp(u'a b'))) == 1
    assert len(matcher(nlp(u'a b'))) == 1
    assert len(matcher(nlp(u'a c'))) == 1
    assert len(matcher(nlp(u'a b c'))) == 1
    assert len(matcher(nlp(u'a b b c'))) == 1
    assert len(matcher(nlp(u'a b b'))) == 1


@pytest.fixture
def text():
    return u"The quick brown fox jumped over the lazy fox"

@pytest.fixture
def heads():
    return [3,2,1,1,0,-1,2,1,-3]

@pytest.fixture
def deps():
    return ['det', 'amod', 'amod', 'nsubj', 'prep', 'pobj', 'det', 'amod']

@pytest.fixture
def dependency_tree_matcher(en_vocab):
    is_brown_yellow = lambda text: bool(re.compile(r'brown|yellow|over').match(text))
    IS_BROWN_YELLOW = en_vocab.add_flag(is_brown_yellow)
    pattern1 = [
        {'SPEC': {'NODE_NAME': 'fox'}, 'PATTERN': {'ORTH': 'fox'}},
        {'SPEC': {'NODE_NAME': 'q', 'NBOR_RELOP': '>', 'NBOR_NAME': 'fox'},'PATTERN': {'LOWER': u'quick'}},
        {'SPEC': {'NODE_NAME': 'r', 'NBOR_RELOP': '>', 'NBOR_NAME': 'fox'}, 'PATTERN': {IS_BROWN_YELLOW: True}}
    ]

    pattern2 = [
        {'SPEC': {'NODE_NAME': 'jumped'}, 'PATTERN': {'ORTH': 'jumped'}},
        {'SPEC': {'NODE_NAME': 'fox', 'NBOR_RELOP': '>', 'NBOR_NAME': 'jumped'},'PATTERN': {'LOWER': u'fox'}},
        {'SPEC': {'NODE_NAME': 'over', 'NBOR_RELOP': '>', 'NBOR_NAME': 'fox'}, 'PATTERN': {IS_BROWN_YELLOW: True}}
    ]
    matcher = DependencyTreeMatcher(en_vocab)
    matcher.add('pattern1', None, pattern1)
    matcher.add('pattern2', None, pattern2)
    return matcher



def test_dependency_tree_matcher_compile(dependency_tree_matcher):
    assert len(dependency_tree_matcher) == 2

def test_dependency_tree_matcher(dependency_tree_matcher,text,heads,deps):
    doc = get_doc(dependency_tree_matcher.vocab,text.split(),heads=heads,deps=deps)
    matches = dependency_tree_matcher(doc)
    assert len(matches) == 2

