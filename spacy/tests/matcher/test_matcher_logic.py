import pytest
import re

from spacy.lang.en import English
from spacy.matcher import Matcher
from spacy.tokens import Doc, Span


pattern1 = [{"ORTH": "A"}, {"ORTH": "A", "OP": "*"}]
pattern2 = [{"ORTH": "A", "OP": "*"}, {"ORTH": "A"}]
pattern3 = [{"ORTH": "A"}, {"ORTH": "A"}]
pattern4 = [{"ORTH": "B"}, {"ORTH": "A", "OP": "*"}, {"ORTH": "B"}]
pattern5 = [{"ORTH": "B", "OP": "*"}, {"ORTH": "A", "OP": "*"}, {"ORTH": "B"}]

re_pattern1 = "AA*"
re_pattern2 = "A*A"
re_pattern3 = "AA"
re_pattern4 = "BA*B"
re_pattern5 = "B*A*B"

longest1 = "A A A A A"
longest2 = "A A A A A"
longest3 = "A A"
longest4 = "B A A A A A B"  # "FIRST" would be "B B"
longest5 = "B B A A A A A B"


@pytest.fixture
def text():
    return "(BBAAAAAB)."


@pytest.fixture
def doc(en_tokenizer, text):
    doc = en_tokenizer(" ".join(text))
    return doc


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
def test_greedy_matching_first(doc, text, pattern, re_pattern):
    """Test that the greedy matching behavior "FIRST" is consistent with
    other re implementations."""
    matcher = Matcher(doc.vocab)
    matcher.add(re_pattern, [pattern], greedy="FIRST")
    matches = matcher(doc)
    re_matches = [m.span() for m in re.finditer(re_pattern, text)]
    for (key, m_s, m_e), (re_s, re_e) in zip(matches, re_matches):
        # matching the string, not the exact position
        assert doc[m_s:m_e].text == doc[re_s:re_e].text


@pytest.mark.parametrize(
    "pattern,longest",
    [
        (pattern1, longest1),
        (pattern2, longest2),
        (pattern3, longest3),
        (pattern4, longest4),
        (pattern5, longest5),
    ],
)
def test_greedy_matching_longest(doc, text, pattern, longest):
    """Test the "LONGEST" greedy matching behavior"""
    matcher = Matcher(doc.vocab)
    matcher.add("RULE", [pattern], greedy="LONGEST")
    matches = matcher(doc)
    for (key, s, e) in matches:
        assert doc[s:e].text == longest


def test_greedy_matching_longest_first(en_tokenizer):
    """Test that "LONGEST" matching prefers the first of two equally long matches"""
    doc = en_tokenizer(" ".join("CCC"))
    matcher = Matcher(doc.vocab)
    pattern = [{"ORTH": "C"}, {"ORTH": "C"}]
    matcher.add("RULE", [pattern], greedy="LONGEST")
    matches = matcher(doc)
    # out of 0-2 and 1-3, the first should be picked
    assert len(matches) == 1
    assert matches[0][1] == 0
    assert matches[0][2] == 2


def test_invalid_greediness(doc, text):
    matcher = Matcher(doc.vocab)
    with pytest.raises(ValueError):
        matcher.add("RULE", [pattern1], greedy="GREEDY")


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
    matcher.add(re_pattern, [pattern], greedy="FIRST")
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
        matcher.add("PATTERN", [pattern])
        matches = matcher(doc)
        if result:
            assert matches, (string, pattern_str)
        else:
            assert not matches, (string, pattern_str)


def test_matcher_end_zero_plus(en_vocab):
    """Test matcher works when patterns end with * operator. (issue 1450)"""
    matcher = Matcher(en_vocab)
    pattern = [{"ORTH": "a"}, {"ORTH": "b", "OP": "*"}]
    matcher.add("TSTEND", [pattern])
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
        [{"LOWER": {"IN": ["zero"]}}],
        [{"LOWER": {"IN": ["one"]}}],
        [{"LOWER": {"IN": ["two"]}}],
    ]
    matcher.add("TEST", patterns)
    doc = Doc(en_vocab, words="zero one two three".split())
    matches = matcher(doc)
    texts = [Span(doc, s, e, label=L).text for L, s, e in matches]
    assert texts == ["zero", "one", "two"]


@pytest.mark.filterwarnings("ignore:\\[W036")
def test_matcher_remove():
    nlp = English()
    matcher = Matcher(nlp.vocab)
    text = "This is a test case."

    pattern = [{"ORTH": "test"}, {"OP": "?"}]
    assert len(matcher) == 0
    matcher.add("Rule", [pattern])
    assert "Rule" in matcher

    # should give two matches
    results1 = matcher(nlp(text))
    assert len(results1) == 2

    # removing once should work
    matcher.remove("Rule")

    # should not return any maches anymore
    results2 = matcher(nlp(text))
    assert len(results2) == 0

    # removing again should throw an error
    with pytest.raises(ValueError):
        matcher.remove("Rule")


def test_matcher_with_alignments_greedy_longest(en_vocab):
    cases = [
        ("aaab", "a* b", [0, 0, 0, 1]),
        ("baab", "b a* b", [0, 1, 1, 2]),
        ("aaab", "a a a b", [0, 1, 2, 3]),
        ("aaab", "a+ b", [0, 0, 0, 1]),
        ("aaba", "a+ b a+", [0, 0, 1, 2]),
        ("aabaa", "a+ b a+", [0, 0, 1, 2, 2]),
        ("aaba", "a+ b a*", [0, 0, 1, 2]),
        ("aaaa", "a*", [0, 0, 0, 0]),
        ("baab", "b a* b b*", [0, 1, 1, 2]),
        ("aabb", "a* b* a*", [0, 0, 1, 1]),
        ("aaab", "a+ a+ a b", [0, 1, 2, 3]),
        ("aaab", "a+ a+ a+ b", [0, 1, 2, 3]),
        ("aaab", "a+ a a b", [0, 1, 2, 3]),
        ("aaab", "a+ a a", [0, 1, 2]),
        ("aaab", "a+ a a?", [0, 1, 2]),
        ("aaaa", "a a a a a?", [0, 1, 2, 3]),
        ("aaab", "a+ a b", [0, 0, 1, 2]),
        ("aaab", "a+ a+ b", [0, 0, 1, 2]),
    ]
    for string, pattern_str, result in cases:
        matcher = Matcher(en_vocab)
        doc = Doc(matcher.vocab, words=list(string))
        pattern = []
        for part in pattern_str.split():
            if part.endswith("+"):
                pattern.append({"ORTH": part[0], "OP": "+"})
            elif part.endswith("*"):
                pattern.append({"ORTH": part[0], "OP": "*"})
            elif part.endswith("?"):
                pattern.append({"ORTH": part[0], "OP": "?"})
            else:
                pattern.append({"ORTH": part})
        matcher.add("PATTERN", [pattern], greedy="LONGEST")
        matches = matcher(doc, with_alignments=True)
        n_matches = len(matches)

        _, s, e, expected = matches[0]

        assert expected == result, (string, pattern_str, s, e, n_matches)


def test_matcher_with_alignments_nongreedy(en_vocab):
    cases = [
        (0, "aaab", "a* b", [[0, 1], [0, 0, 1], [0, 0, 0, 1], [1]]),
        (1, "baab", "b a* b", [[0, 1, 1, 2]]),
        (2, "aaab", "a a a b", [[0, 1, 2, 3]]),
        (3, "aaab", "a+ b", [[0, 1], [0, 0, 1], [0, 0, 0, 1]]),
        (4, "aaba", "a+ b a+", [[0, 1, 2], [0, 0, 1, 2]]),
        (
            5,
            "aabaa",
            "a+ b a+",
            [[0, 1, 2], [0, 0, 1, 2], [0, 0, 1, 2, 2], [0, 1, 2, 2]],
        ),
        (6, "aaba", "a+ b a*", [[0, 1], [0, 0, 1], [0, 0, 1, 2], [0, 1, 2]]),
        (7, "aaaa", "a*", [[0], [0, 0], [0, 0, 0], [0, 0, 0, 0]]),
        (8, "baab", "b a* b b*", [[0, 1, 1, 2]]),
        (
            9,
            "aabb",
            "a* b* a*",
            [[1], [2], [2, 2], [0, 1], [0, 0, 1], [0, 0, 1, 1], [0, 1, 1], [1, 1]],
        ),
        (10, "aaab", "a+ a+ a b", [[0, 1, 2, 3]]),
        (11, "aaab", "a+ a+ a+ b", [[0, 1, 2, 3]]),
        (12, "aaab", "a+ a a b", [[0, 1, 2, 3]]),
        (13, "aaab", "a+ a a", [[0, 1, 2]]),
        (14, "aaab", "a+ a a?", [[0, 1], [0, 1, 2]]),
        (15, "aaaa", "a a a a a?", [[0, 1, 2, 3]]),
        (16, "aaab", "a+ a b", [[0, 1, 2], [0, 0, 1, 2]]),
        (17, "aaab", "a+ a+ b", [[0, 1, 2], [0, 0, 1, 2]]),
    ]
    for case_id, string, pattern_str, results in cases:
        matcher = Matcher(en_vocab)
        doc = Doc(matcher.vocab, words=list(string))
        pattern = []
        for part in pattern_str.split():
            if part.endswith("+"):
                pattern.append({"ORTH": part[0], "OP": "+"})
            elif part.endswith("*"):
                pattern.append({"ORTH": part[0], "OP": "*"})
            elif part.endswith("?"):
                pattern.append({"ORTH": part[0], "OP": "?"})
            else:
                pattern.append({"ORTH": part})

        matcher.add("PATTERN", [pattern])
        matches = matcher(doc, with_alignments=True)
        n_matches = len(matches)

        for _, s, e, expected in matches:
            assert expected in results, (case_id, string, pattern_str, s, e, n_matches)
            assert len(expected) == e - s
