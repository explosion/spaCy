# coding: utf-8
from __future__ import unicode_literals

import pytest
import re
from spacy.matcher import Matcher
from spacy.tokens import Doc, Span


pattern1 = [{"ORTH": "A", "OP": "1"}, {"ORTH": "A", "OP": "*"}]
pattern2 = [{"ORTH": "A", "OP": "*"}, {"ORTH": "A", "OP": "1"}]
pattern3 = [{"ORTH": "A", "OP": "1"}, {"ORTH": "A", "OP": "1"}]
pattern4 = [
    {"ORTH": "B", "OP": "1"},
    {"ORTH": "A", "OP": "*"},
    {"ORTH": "B", "OP": "1"},
]
pattern5 = [
    {"ORTH": "B", "OP": "*"},
    {"ORTH": "A", "OP": "*"},
    {"ORTH": "B", "OP": "1"},
]

re_pattern1 = "AA*"
re_pattern2 = "A*A"
re_pattern3 = "AA"
re_pattern4 = "BA*B"
re_pattern5 = "B*A*B"


@pytest.fixture
def text():
    return "(ABBAAAAAB)."


@pytest.fixture
def doc(en_tokenizer, text):
    doc = en_tokenizer(" ".join(text))
    return doc


@pytest.mark.parametrize(
    "pattern,re_pattern",
    [
        pytest.param(pattern1, re_pattern1, marks=pytest.mark.xfail()),
        pytest.param(pattern2, re_pattern2, marks=pytest.mark.xfail()),
        pytest.param(pattern3, re_pattern3, marks=pytest.mark.xfail()),
        (pattern4, re_pattern4),
        pytest.param(pattern5, re_pattern5, marks=pytest.mark.xfail()),
    ],
)
def test_greedy_matching(doc, text, pattern, re_pattern):
    """Test that the greedy matching behavior of the * op is consistant with
    other re implementations."""
    matcher = Matcher(doc.vocab)
    matcher.add(re_pattern, None, pattern)
    matches = matcher(doc)
    re_matches = [m.span() for m in re.finditer(re_pattern, text)]
    for match, re_match in zip(matches, re_matches):
        assert match[1:] == re_match


@pytest.mark.xfail
@pytest.mark.parametrize(
    "pattern,re_pattern",
    [
        (pattern1, re_pattern1),
        (pattern2, re_pattern2),
        (pattern3, re_pattern3),
        (pattern4, re_pattern4),
        (pattern5, re_pattern5),
    ],
)
def test_match_consuming(doc, text, pattern, re_pattern):
    """Test that matcher.__call__ consumes tokens on a match similar to
    re.findall."""
    matcher = Matcher(doc.vocab)
    matcher.add(re_pattern, None, pattern)
    matches = matcher(doc)
    re_matches = [m.span() for m in re.finditer(re_pattern, text)]
    assert len(matches) == len(re_matches)


def test_operator_combos(en_vocab):
    cases = [
        ("aaab", "a a a b", True),
        ("aaab", "a+ b", True),
        ("aaab", "a+ a+ b", True),
        ("aaab", "a+ a+ a b", True),
        ("aaab", "a+ a+ a+ b", True),
        ("aaab", "a+ a a b", True),
        ("aaab", "a+ a a", True),
        ("aaab", "a+", True),
        ("aaa", "a+ b", False),
        ("aaa", "a+ a+ b", False),
        ("aaa", "a+ a+ a+ b", False),
        ("aaa", "a+ a b", False),
        ("aaa", "a+ a a b", False),
        ("aaab", "a+ a a", True),
        ("aaab", "a+", True),
        ("aaab", "a+ a b", True),
    ]
    for string, pattern_str, result in cases:
        matcher = Matcher(en_vocab)
        doc = Doc(matcher.vocab, words=list(string))
        pattern = []
        for part in pattern_str.split():
            if part.endswith("+"):
                pattern.append({"ORTH": part[0], "OP": "+"})
            else:
                pattern.append({"ORTH": part})
        matcher.add("PATTERN", None, pattern)
        matches = matcher(doc)
        if result:
            assert matches, (string, pattern_str)
        else:
            assert not matches, (string, pattern_str)


def test_matcher_end_zero_plus(en_vocab):
    """Test matcher works when patterns end with * operator. (issue 1450)"""
    matcher = Matcher(en_vocab)
    pattern = [{"ORTH": "a"}, {"ORTH": "b", "OP": "*"}]
    matcher.add("TSTEND", None, pattern)
    nlp = lambda string: Doc(matcher.vocab, words=string.split())
    assert len(matcher(nlp("a"))) == 1
    assert len(matcher(nlp("a b"))) == 2
    assert len(matcher(nlp("a c"))) == 1
    assert len(matcher(nlp("a b c"))) == 2
    assert len(matcher(nlp("a b b c"))) == 3
    assert len(matcher(nlp("a b b"))) == 3


def test_matcher_sets_return_correct_tokens(en_vocab):
    matcher = Matcher(en_vocab)
    patterns = [
        [{'LOWER': {'IN': ["zero"]}}],
        [{'LOWER': {'IN': ["one"]}}],
        [{'LOWER': {'IN': ["two"]}}],
    ]
    matcher.add('TEST', None, *patterns)
    doc = Doc(en_vocab, words="zero one two three".split())
    matches = matcher(doc)
    texts = [Span(doc, s, e, label=L).text for L, s, e in matches]
    assert texts == ['zero', 'one', 'two']
