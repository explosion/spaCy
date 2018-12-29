import pytest
import spacy
from spacy.matcher import Matcher

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
def test_issue3009_patterns_individually(doc, matcher, pattern):
    """Test problem with matcher quantifiers"""
    matcher.add(pattern[0], None, *pattern[1])
    matches = matcher(doc)
    assert matches
