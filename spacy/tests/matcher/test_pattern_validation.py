import pytest

from spacy.errors import MatchPatternError
from spacy.matcher import Matcher
from spacy.schemas import validate_token_pattern

# (pattern, num errors with validation, num errors identified with minimal
#  checks)
TEST_PATTERNS = [
    # Bad patterns flagged in all cases
    ([{"XX": "foo"}], 1, 1),
    ([{"IS_ALPHA": {"==": True}}, {"LIKE_NUM": None}], 2, 1),
    (
        [{"IS_PUNCT": True, "OP": "$"}],
        2,
        1,
    ),  # v2: union reports 2 errors (enum + pattern)
    ([{"_": "foo"}], 1, 1),
    ('[{"TEXT": "foo"}, {"LOWER": "bar"}]', 1, 1),
    ([{"ENT_IOB": "foo"}], 1, 1),
    ([1, 2, 3], 3, 1),
    ([{"TEXT": "foo", "OP": "{,}"}], 2, 1),  # v2: union reports 2 errors
    ([{"TEXT": "foo", "OP": "{,4}4"}], 2, 1),  # v2: union reports 2 errors
    ([{"TEXT": "foo", "OP": "{a,3}"}], 2, 1),  # v2: union reports 2 errors
    ([{"TEXT": "foo", "OP": "{a}"}], 2, 1),  # v2: union reports 2 errors
    ([{"TEXT": "foo", "OP": "{,a}"}], 2, 1),  # v2: union reports 2 errors
    ([{"TEXT": "foo", "OP": "{1,2,3}"}], 2, 1),  # v2: union reports 2 errors
    ([{"TEXT": "foo", "OP": "{1, 3}"}], 2, 1),  # v2: union reports 2 errors
    ([{"TEXT": "foo", "OP": "{-2}"}], 2, 1),  # v2: union reports 2 errors
    # Bad patterns flagged outside of Matcher
    (
        [{"_": {"foo": "bar", "baz": {"IN": "foo"}}}],
        7,
        0,
    ),  # v2: more detailed union errors
    # Bad patterns not flagged with minimal checks
    (
        [{"LENGTH": "2", "TEXT": 2}, {"LOWER": "test"}],
        5,
        0,
    ),  # v2: more detailed union errors
    (
        [{"LENGTH": {"IN": [1, 2, "3"]}}, {"POS": {"IN": "VERB"}}],
        5,
        0,
    ),  # v2: more detailed union errors
    ([{"LENGTH": {"VALUE": 5}}], 3, 0),  # v2: more detailed union errors
    ([{"TEXT": {"VALUE": "foo"}}], 2, 0),
    ([{"IS_DIGIT": -1}], 1, 0),
    ([{"ORTH": -1}], 2, 0),  # v2: union reports 2 errors
    ([{"ENT_ID": -1}], 2, 0),  # v2: union reports 2 errors
    ([{"ENT_KB_ID": -1}], 2, 0),  # v2: union reports 2 errors
    # Good patterns
    ([{"TEXT": "foo"}, {"LOWER": "bar"}], 0, 0),
    ([{"LEMMA": {"IN": ["love", "like"]}}, {"POS": "DET", "OP": "?"}], 0, 0),
    ([{"LIKE_NUM": True, "LENGTH": {">=": 5}}], 0, 0),
    ([{"LENGTH": 2}], 0, 0),
    ([{"LOWER": {"REGEX": "^X", "NOT_IN": ["XXX", "XY"]}}], 0, 0),
    ([{"NORM": "a"}, {"POS": {"IN": ["NOUN"]}}], 0, 0),
    ([{"_": {"foo": {"NOT_IN": ["bar", "baz"]}, "a": 5, "b": {">": 10}}}], 0, 0),
    ([{"orth": "foo"}], 0, 0),  # prev: xfail
    ([{"IS_SENT_START": True}], 0, 0),
    ([{"SENT_START": True}], 0, 0),
    ([{"ENT_ID": "STRING"}], 0, 0),
    ([{"ENT_KB_ID": "STRING"}], 0, 0),
    ([{"TEXT": "ha", "OP": "{3}"}], 0, 0),
]


@pytest.mark.parametrize(
    "pattern",
    [[{"XX": "y"}], [{"LENGTH": "2"}], [{"TEXT": {"IN": 5}}], [{"text": {"in": 6}}]],
)
def test_matcher_pattern_validation(en_vocab, pattern):
    matcher = Matcher(en_vocab, validate=True)
    with pytest.raises(MatchPatternError):
        matcher.add("TEST", [pattern])


@pytest.mark.parametrize("pattern,n_errors,_", TEST_PATTERNS)
def test_pattern_validation(pattern, n_errors, _):
    errors = validate_token_pattern(pattern)
    assert len(errors) == n_errors


@pytest.mark.parametrize("pattern,n_errors,n_min_errors", TEST_PATTERNS)
def test_minimal_pattern_validation(en_vocab, pattern, n_errors, n_min_errors):
    matcher = Matcher(en_vocab)
    if n_min_errors > 0:
        with pytest.raises(ValueError):
            matcher.add("TEST", [pattern])
    elif n_errors == 0:
        matcher.add("TEST", [pattern])


def test_pattern_errors(en_vocab):
    matcher = Matcher(en_vocab)
    # normalize "regex" to upper like "text"
    matcher.add("TEST1", [[{"text": {"regex": "regex"}}]])
    # error if subpattern attribute isn't recognized and processed
    with pytest.raises(MatchPatternError):
        matcher.add("TEST2", [[{"TEXT": {"XX": "xx"}}]])
