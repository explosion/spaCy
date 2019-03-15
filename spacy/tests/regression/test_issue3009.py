# coding: utf-8
from __future__ import unicode_literals

import pytest
from spacy.matcher import Matcher
from spacy.tokens import Doc


PATTERNS = [
    ("1", [[{"LEMMA": "have"}, {"LOWER": "to"}, {"LOWER": "do"}, {"POS": "ADP"}]]),
    (
        "2",
        [
            [
                {"LEMMA": "have"},
                {"IS_ASCII": True, "IS_PUNCT": False, "OP": "*"},
                {"LOWER": "to"},
                {"LOWER": "do"},
                {"POS": "ADP"},
            ]
        ],
    ),
    (
        "3",
        [
            [
                {"LEMMA": "have"},
                {"IS_ASCII": True, "IS_PUNCT": False, "OP": "?"},
                {"LOWER": "to"},
                {"LOWER": "do"},
                {"POS": "ADP"},
            ]
        ],
    ),
]


@pytest.fixture
def doc(en_tokenizer):
    doc = en_tokenizer("also has to do with")
    doc[0].tag_ = "RB"
    doc[1].tag_ = "VBZ"
    doc[2].tag_ = "TO"
    doc[3].tag_ = "VB"
    doc[4].tag_ = "IN"
    return doc


@pytest.fixture
def matcher(en_tokenizer):
    return Matcher(en_tokenizer.vocab)


@pytest.mark.parametrize("pattern", PATTERNS)
def test_issue3009(doc, matcher, pattern):
    """Test problem with matcher quantifiers"""
    matcher.add(pattern[0], None, *pattern[1])
    matches = matcher(doc)
    assert matches


def test_issue2464(matcher):
    """Test problem with successive ?. This is the same bug, so putting it here."""
    doc = Doc(matcher.vocab, words=["a", "b"])
    matcher.add("4", None, [{"OP": "?"}, {"OP": "?"}])
    matches = matcher(doc)
    assert len(matches) == 3
