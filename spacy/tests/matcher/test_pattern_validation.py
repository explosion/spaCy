# coding: utf-8
from __future__ import unicode_literals

import pytest
from spacy.matcher import Matcher
from spacy.matcher._schemas import TOKEN_PATTERN_SCHEMA
from spacy.errors import MatchPatternError
from spacy.util import get_json_validator, validate_json


@pytest.fixture
def validator():
    return get_json_validator(TOKEN_PATTERN_SCHEMA)


@pytest.mark.parametrize(
    "pattern", [[{"XX": "y"}, {"LENGTH": "2"}, {"TEXT": {"IN": 5}}]]
)
def test_matcher_pattern_validation(en_vocab, pattern):
    matcher = Matcher(en_vocab, validate=True)
    with pytest.raises(MatchPatternError):
        matcher.add("TEST", None, pattern)


@pytest.mark.parametrize(
    "pattern,n_errors",
    [
        # Bad patterns
        ([{"XX": "foo"}], 1),
        ([{"LENGTH": "2", "TEXT": 2}, {"LOWER": "test"}], 2),
        ([{"LENGTH": {"IN": [1, 2, "3"]}}, {"POS": {"IN": "VERB"}}], 2),
        ([{"IS_ALPHA": {"==": True}}, {"LIKE_NUM": None}], 2),
        ([{"TEXT": {"VALUE": "foo"}}], 1),
        ([{"LENGTH": {"VALUE": 5}}], 1),
        ([{"_": "foo"}], 1),
        ([{"_": {"foo": "bar", "baz": {"IN": "foo"}}}], 1),
        ([{"IS_PUNCT": True, "OP": "$"}], 1),
        # Good patterns
        ([{"TEXT": "foo"}, {"LOWER": "bar"}], 0),
        ([{"LEMMA": {"IN": ["love", "like"]}}, {"POS": "DET", "OP": "?"}], 0),
        ([{"LIKE_NUM": True, "LENGTH": {">=": 5}}], 0),
        ([{"LOWER": {"REGEX": "^X", "NOT_IN": ["XXX", "XY"]}}], 0),
        ([{"_": {"foo": {"NOT_IN": ["bar", "baz"]}, "a": 5, "b": {">": 10}}}], 0),
    ],
)
def test_pattern_validation(validator, pattern, n_errors):
    errors = validate_json(pattern, validator)
    assert len(errors) == n_errors
