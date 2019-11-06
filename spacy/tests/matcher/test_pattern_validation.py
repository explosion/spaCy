# coding: utf-8
from __future__ import unicode_literals

import pytest
from spacy.matcher import Matcher
from spacy.matcher._schemas import TOKEN_PATTERN_SCHEMA
from spacy.errors import MatchPatternError
from spacy.util import get_json_validator, validate_json

# (pattern, num errors with validation, num errors identified with minimal
#  checks)
TEST_PATTERNS = [
    # Bad patterns flagged in all cases
    ([{"XX": "foo"}], 1, 1),
    ([{"IS_ALPHA": {"==": True}}, {"LIKE_NUM": None}], 2, 1),
    ([{"IS_PUNCT": True, "OP": "$"}], 1, 1),
    ([{"_": "foo"}], 1, 1),
    ('[{"TEXT": "foo"}, {"LOWER": "bar"}]', 1, 1),
    ([1, 2, 3], 3, 1),
    # Bad patterns flagged outside of Matcher
    ([{"_": {"foo": "bar", "baz": {"IN": "foo"}}}], 1, 0),
    # Bad patterns not flagged with minimal checks
    ([{"LENGTH": "2", "TEXT": 2}, {"LOWER": "test"}], 2, 0),
    ([{"LENGTH": {"IN": [1, 2, "3"]}}, {"POS": {"IN": "VERB"}}], 2, 0),
    ([{"LENGTH": {"VALUE": 5}}], 1, 0),
    ([{"TEXT": {"VALUE": "foo"}}], 1, 0),
    ([{"IS_DIGIT": -1}], 1, 0),
    ([{"ORTH": -1}], 1, 0),
    # Good patterns
    ([{"TEXT": "foo"}, {"LOWER": "bar"}], 0, 0),
    ([{"LEMMA": {"IN": ["love", "like"]}}, {"POS": "DET", "OP": "?"}], 0, 0),
    ([{"LIKE_NUM": True, "LENGTH": {">=": 5}}], 0, 0),
    ([{"LENGTH": 2}], 0, 0),
    ([{"LOWER": {"REGEX": "^X", "NOT_IN": ["XXX", "XY"]}}], 0, 0),
    ([{"NORM": "a"}, {"POS": {"IN": ["NOUN"]}}], 0, 0),
    ([{"_": {"foo": {"NOT_IN": ["bar", "baz"]}, "a": 5, "b": {">": 10}}}], 0, 0),
]

XFAIL_TEST_PATTERNS = [([{"orth": "foo"}], 0, 0)]


@pytest.fixture
def validator():
    return get_json_validator(TOKEN_PATTERN_SCHEMA)


@pytest.mark.parametrize(
    "pattern", [[{"XX": "y"}, {"LENGTH": "2"}, {"TEXT": {"IN": 5}}]]
)
def test_matcher_pattern_validation(en_vocab, pattern):
    matcher = Matcher(en_vocab, validate=True)
    with pytest.raises(MatchPatternError):
        matcher.add("TEST", [pattern])


@pytest.mark.parametrize("pattern,n_errors,_", TEST_PATTERNS)
def test_pattern_validation(validator, pattern, n_errors, _):
    errors = validate_json(pattern, validator)
    assert len(errors) == n_errors


@pytest.mark.xfail
@pytest.mark.parametrize("pattern,n_errors,_", XFAIL_TEST_PATTERNS)
def test_xfail_pattern_validation(validator, pattern, n_errors, _):
    errors = validate_json(pattern, validator)
    assert len(errors) == n_errors


@pytest.mark.parametrize("pattern,n_errors,n_min_errors", TEST_PATTERNS)
def test_minimal_pattern_validation(en_vocab, pattern, n_errors, n_min_errors):
    matcher = Matcher(en_vocab)
    if n_min_errors > 0:
        with pytest.raises(ValueError):
            matcher.add("TEST", [pattern])
    elif n_errors == 0:
        matcher.add("TEST", [pattern])
