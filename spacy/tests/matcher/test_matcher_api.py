# coding: utf-8
from __future__ import unicode_literals

import pytest
import re
from spacy.matcher import Matcher, DependencyMatcher
from spacy.tokens import Doc, Token


@pytest.fixture
def matcher(en_vocab):
    rules = {
        "JS": [[{"ORTH": "JavaScript"}]],
        "GoogleNow": [[{"ORTH": "Google"}, {"ORTH": "Now"}]],
        "Java": [[{"LOWER": "java"}]],
    }
    matcher = Matcher(en_vocab)
    for key, patterns in rules.items():
        matcher.add(key, None, *patterns)
    return matcher


def test_matcher_from_api_docs(en_vocab):
    matcher = Matcher(en_vocab)
    pattern = [{"ORTH": "test"}]
    assert len(matcher) == 0
    matcher.add("Rule", None, pattern)
    assert len(matcher) == 1
    matcher.remove("Rule")
    assert "Rule" not in matcher
    matcher.add("Rule", None, pattern)
    assert "Rule" in matcher
    on_match, patterns = matcher.get("Rule")
    assert len(patterns[0])


def test_matcher_from_usage_docs(en_vocab):
    text = "Wow 😀 This is really cool! 😂 😂"
    doc = Doc(en_vocab, words=text.split(" "))
    pos_emoji = ["😀", "😃", "😂", "🤣", "😊", "😍"]
    pos_patterns = [[{"ORTH": emoji}] for emoji in pos_emoji]

    def label_sentiment(matcher, doc, i, matches):
        match_id, start, end = matches[i]
        if doc.vocab.strings[match_id] == "HAPPY":
            doc.sentiment += 0.1
        span = doc[start:end]
        with doc.retokenize() as retokenizer:
            retokenizer.merge(span)
        token = doc[start]
        token.vocab[token.text].norm_ = "happy emoji"

    matcher = Matcher(en_vocab)
    matcher.add("HAPPY", label_sentiment, *pos_patterns)
    matcher(doc)
    assert doc.sentiment != 0
    assert doc[1].norm_ == "happy emoji"


def test_matcher_len_contains(matcher):
    assert len(matcher) == 3
    matcher.add("TEST", None, [{"ORTH": "test"}])
    assert "TEST" in matcher
    assert "TEST2" not in matcher


def test_matcher_no_match(matcher):
    doc = Doc(matcher.vocab, words=["I", "like", "cheese", "."])
    assert matcher(doc) == []


def test_matcher_match_start(matcher):
    doc = Doc(matcher.vocab, words=["JavaScript", "is", "good"])
    assert matcher(doc) == [(matcher.vocab.strings["JS"], 0, 1)]


def test_matcher_match_end(matcher):
    words = ["I", "like", "java"]
    doc = Doc(matcher.vocab, words=words)
    assert matcher(doc) == [(doc.vocab.strings["Java"], 2, 3)]


def test_matcher_match_middle(matcher):
    words = ["I", "like", "Google", "Now", "best"]
    doc = Doc(matcher.vocab, words=words)
    assert matcher(doc) == [(doc.vocab.strings["GoogleNow"], 2, 4)]


def test_matcher_match_multi(matcher):
    words = ["I", "like", "Google", "Now", "and", "java", "best"]
    doc = Doc(matcher.vocab, words=words)
    assert matcher(doc) == [
        (doc.vocab.strings["GoogleNow"], 2, 4),
        (doc.vocab.strings["Java"], 5, 6),
    ]


def test_matcher_empty_dict(en_vocab):
    """Test matcher allows empty token specs, meaning match on any token."""
    matcher = Matcher(en_vocab)
    doc = Doc(matcher.vocab, words=["a", "b", "c"])
    matcher.add("A.C", None, [{"ORTH": "a"}, {}, {"ORTH": "c"}])
    matches = matcher(doc)
    assert len(matches) == 1
    assert matches[0][1:] == (0, 3)
    matcher = Matcher(en_vocab)
    matcher.add("A.", None, [{"ORTH": "a"}, {}])
    matches = matcher(doc)
    assert matches[0][1:] == (0, 2)


def test_matcher_operator_shadow(en_vocab):
    matcher = Matcher(en_vocab)
    doc = Doc(matcher.vocab, words=["a", "b", "c"])
    pattern = [{"ORTH": "a"}, {"IS_ALPHA": True, "OP": "+"}, {"ORTH": "c"}]
    matcher.add("A.C", None, pattern)
    matches = matcher(doc)
    assert len(matches) == 1
    assert matches[0][1:] == (0, 3)


def test_matcher_match_zero(matcher):
    words1 = 'He said , " some words " ...'.split()
    words2 = 'He said , " some three words " ...'.split()
    pattern1 = [
        {"ORTH": '"'},
        {"OP": "!", "IS_PUNCT": True},
        {"OP": "!", "IS_PUNCT": True},
        {"ORTH": '"'},
    ]
    pattern2 = [
        {"ORTH": '"'},
        {"IS_PUNCT": True},
        {"IS_PUNCT": True},
        {"IS_PUNCT": True},
        {"ORTH": '"'},
    ]
    matcher.add("Quote", None, pattern1)
    doc = Doc(matcher.vocab, words=words1)
    assert len(matcher(doc)) == 1
    doc = Doc(matcher.vocab, words=words2)
    assert len(matcher(doc)) == 0
    matcher.add("Quote", None, pattern2)
    assert len(matcher(doc)) == 0


def test_matcher_match_zero_plus(matcher):
    words = 'He said , " some words " ...'.split()
    pattern = [{"ORTH": '"'}, {"OP": "*", "IS_PUNCT": False}, {"ORTH": '"'}]
    matcher = Matcher(matcher.vocab)
    matcher.add("Quote", None, pattern)
    doc = Doc(matcher.vocab, words=words)
    assert len(matcher(doc)) == 1


def test_matcher_match_one_plus(matcher):
    control = Matcher(matcher.vocab)
    control.add("BasicPhilippe", None, [{"ORTH": "Philippe"}])
    doc = Doc(control.vocab, words=["Philippe", "Philippe"])
    m = control(doc)
    assert len(m) == 2
    matcher.add(
        "KleenePhilippe",
        None,
        [{"ORTH": "Philippe", "OP": "1"}, {"ORTH": "Philippe", "OP": "+"}],
    )
    m = matcher(doc)
    assert len(m) == 1


def test_matcher_any_token_operator(en_vocab):
    """Test that patterns with "any token" {} work with operators."""
    matcher = Matcher(en_vocab)
    matcher.add("TEST", None, [{"ORTH": "test"}, {"OP": "*"}])
    doc = Doc(en_vocab, words=["test", "hello", "world"])
    matches = [doc[start:end].text for _, start, end in matcher(doc)]
    assert len(matches) == 3
    assert matches[0] == "test"
    assert matches[1] == "test hello"
    assert matches[2] == "test hello world"


def test_matcher_extension_attribute(en_vocab):
    matcher = Matcher(en_vocab)
    get_is_fruit = lambda token: token.text in ("apple", "banana")
    Token.set_extension("is_fruit", getter=get_is_fruit, force=True)
    pattern = [{"ORTH": "an"}, {"_": {"is_fruit": True}}]
    matcher.add("HAVING_FRUIT", None, pattern)
    doc = Doc(en_vocab, words=["an", "apple"])
    matches = matcher(doc)
    assert len(matches) == 1
    doc = Doc(en_vocab, words=["an", "aardvark"])
    matches = matcher(doc)
    assert len(matches) == 0


def test_matcher_set_value(en_vocab):
    matcher = Matcher(en_vocab)
    pattern = [{"ORTH": {"IN": ["an", "a"]}}]
    matcher.add("A_OR_AN", None, pattern)
    doc = Doc(en_vocab, words=["an", "a", "apple"])
    matches = matcher(doc)
    assert len(matches) == 2
    doc = Doc(en_vocab, words=["aardvark"])
    matches = matcher(doc)
    assert len(matches) == 0


def test_matcher_set_value_operator(en_vocab):
    matcher = Matcher(en_vocab)
    pattern = [{"ORTH": {"IN": ["a", "the"]}, "OP": "?"}, {"ORTH": "house"}]
    matcher.add("DET_HOUSE", None, pattern)
    doc = Doc(en_vocab, words=["In", "a", "house"])
    matches = matcher(doc)
    assert len(matches) == 2
    doc = Doc(en_vocab, words=["my", "house"])
    matches = matcher(doc)
    assert len(matches) == 1


def test_matcher_regex(en_vocab):
    matcher = Matcher(en_vocab)
    pattern = [{"ORTH": {"REGEX": r"(?:a|an)"}}]
    matcher.add("A_OR_AN", None, pattern)
    doc = Doc(en_vocab, words=["an", "a", "hi"])
    matches = matcher(doc)
    assert len(matches) == 2
    doc = Doc(en_vocab, words=["bye"])
    matches = matcher(doc)
    assert len(matches) == 0


def test_matcher_regex_shape(en_vocab):
    matcher = Matcher(en_vocab)
    pattern = [{"SHAPE": {"REGEX": r"^[^x]+$"}}]
    matcher.add("NON_ALPHA", None, pattern)
    doc = Doc(en_vocab, words=["99", "problems", "!"])
    matches = matcher(doc)
    assert len(matches) == 2
    doc = Doc(en_vocab, words=["bye"])
    matches = matcher(doc)
    assert len(matches) == 0


def test_matcher_compare_length(en_vocab):
    matcher = Matcher(en_vocab)
    pattern = [{"LENGTH": {">=": 2}}]
    matcher.add("LENGTH_COMPARE", None, pattern)
    doc = Doc(en_vocab, words=["a", "aa", "aaa"])
    matches = matcher(doc)
    assert len(matches) == 2
    doc = Doc(en_vocab, words=["a"])
    matches = matcher(doc)
    assert len(matches) == 0


def test_matcher_extension_set_membership(en_vocab):
    matcher = Matcher(en_vocab)
    get_reversed = lambda token: "".join(reversed(token.text))
    Token.set_extension("reversed", getter=get_reversed, force=True)
    pattern = [{"_": {"reversed": {"IN": ["eyb", "ih"]}}}]
    matcher.add("REVERSED", None, pattern)
    doc = Doc(en_vocab, words=["hi", "bye", "hello"])
    matches = matcher(doc)
    assert len(matches) == 2
    doc = Doc(en_vocab, words=["aardvark"])
    matches = matcher(doc)
    assert len(matches) == 0


@pytest.fixture
def text():
    return "The quick brown fox jumped over the lazy fox"


@pytest.fixture
def heads():
    return [3, 2, 1, 1, 0, -1, 2, 1, -3]


@pytest.fixture
def deps():
    return ["det", "amod", "amod", "nsubj", "prep", "pobj", "det", "amod"]


@pytest.fixture
def dependency_matcher(en_vocab):
    def is_brown_yellow(text):
        return bool(re.compile(r"brown|yellow|over").match(text))

    IS_BROWN_YELLOW = en_vocab.add_flag(is_brown_yellow)

    pattern1 = [
        {"SPEC": {"NODE_NAME": "fox"}, "PATTERN": {"ORTH": "fox"}},
        {
            "SPEC": {"NODE_NAME": "q", "NBOR_RELOP": ">", "NBOR_NAME": "fox"},
            "PATTERN": {"ORTH": "quick", "DEP": "amod"},
        },
        {
            "SPEC": {"NODE_NAME": "r", "NBOR_RELOP": ">", "NBOR_NAME": "fox"},
            "PATTERN": {IS_BROWN_YELLOW: True},
        },
    ]

    pattern2 = [
        {"SPEC": {"NODE_NAME": "jumped"}, "PATTERN": {"ORTH": "jumped"}},
        {
            "SPEC": {"NODE_NAME": "fox", "NBOR_RELOP": ">", "NBOR_NAME": "jumped"},
            "PATTERN": {"ORTH": "fox"},
        },
        {
            "SPEC": {"NODE_NAME": "quick", "NBOR_RELOP": ".", "NBOR_NAME": "jumped"},
            "PATTERN": {"ORTH": "fox"},
        },
    ]

    pattern3 = [
        {"SPEC": {"NODE_NAME": "jumped"}, "PATTERN": {"ORTH": "jumped"}},
        {
            "SPEC": {"NODE_NAME": "fox", "NBOR_RELOP": ">", "NBOR_NAME": "jumped"},
            "PATTERN": {"ORTH": "fox"},
        },
        {
            "SPEC": {"NODE_NAME": "r", "NBOR_RELOP": ">>", "NBOR_NAME": "fox"},
            "PATTERN": {"ORTH": "brown"},
        },
    ]

    matcher = DependencyMatcher(en_vocab)
    matcher.add("pattern1", None, pattern1)
    matcher.add("pattern2", None, pattern2)
    matcher.add("pattern3", None, pattern3)

    return matcher


def test_dependency_matcher_compile(dependency_matcher):
    assert len(dependency_matcher) == 3


# def test_dependency_matcher(dependency_matcher, text, heads, deps):
#     doc = get_doc(dependency_matcher.vocab, text.split(), heads=heads, deps=deps)
#     matches = dependency_matcher(doc)
#     assert matches[0][1] == [[3, 1, 2]]
#     assert matches[1][1] == [[4, 3, 3]]
#     assert matches[2][1] == [[4, 3, 2]]
