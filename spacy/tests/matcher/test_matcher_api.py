import pytest
from mock import Mock
from spacy.matcher import Matcher
from spacy.tokens import Doc, Token, Span

from ..doc.test_underscore import clean_underscore  # noqa: F401


@pytest.fixture
def matcher(en_vocab):
    rules = {
        "JS": [[{"ORTH": "JavaScript"}]],
        "GoogleNow": [[{"ORTH": "Google"}, {"ORTH": "Now"}]],
        "Java": [[{"LOWER": "java"}]],
    }
    matcher = Matcher(en_vocab)
    for key, patterns in rules.items():
        matcher.add(key, patterns)
    return matcher


def test_matcher_from_api_docs(en_vocab):
    matcher = Matcher(en_vocab)
    pattern = [{"ORTH": "test"}]
    assert len(matcher) == 0
    matcher.add("Rule", [pattern])
    assert len(matcher) == 1
    matcher.remove("Rule")
    assert "Rule" not in matcher
    matcher.add("Rule", [pattern])
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
    matcher.add("HAPPY", pos_patterns, on_match=label_sentiment)
    matcher(doc)
    assert doc.sentiment != 0
    assert doc[1].norm_ == "happy emoji"


def test_matcher_len_contains(matcher):
    assert len(matcher) == 3
    matcher.add("TEST", [[{"ORTH": "test"}]])
    assert "TEST" in matcher
    assert "TEST2" not in matcher


def test_matcher_add_new_api(en_vocab):
    doc = Doc(en_vocab, words=["a", "b"])
    patterns = [[{"TEXT": "a"}], [{"TEXT": "a"}, {"TEXT": "b"}]]
    matcher = Matcher(en_vocab)
    on_match = Mock()
    matcher = Matcher(en_vocab)
    matcher.add("NEW_API", patterns)
    assert len(matcher(doc)) == 2
    matcher = Matcher(en_vocab)
    on_match = Mock()
    matcher.add("NEW_API_CALLBACK", patterns, on_match=on_match)
    assert len(matcher(doc)) == 2
    assert on_match.call_count == 2


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
    matcher.add("A.C", [[{"ORTH": "a"}, {}, {"ORTH": "c"}]])
    matches = matcher(doc)
    assert len(matches) == 1
    assert matches[0][1:] == (0, 3)
    matcher = Matcher(en_vocab)
    matcher.add("A.", [[{"ORTH": "a"}, {}]])
    matches = matcher(doc)
    assert matches[0][1:] == (0, 2)


def test_matcher_operator_shadow(en_vocab):
    matcher = Matcher(en_vocab)
    doc = Doc(matcher.vocab, words=["a", "b", "c"])
    pattern = [{"ORTH": "a"}, {"IS_ALPHA": True, "OP": "+"}, {"ORTH": "c"}]
    matcher.add("A.C", [pattern])
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
    matcher.add("Quote", [pattern1])
    doc = Doc(matcher.vocab, words=words1)
    assert len(matcher(doc)) == 1
    doc = Doc(matcher.vocab, words=words2)
    assert len(matcher(doc)) == 0
    matcher.add("Quote", [pattern2])
    assert len(matcher(doc)) == 0


def test_matcher_match_zero_plus(matcher):
    words = 'He said , " some words " ...'.split()
    pattern = [{"ORTH": '"'}, {"OP": "*", "IS_PUNCT": False}, {"ORTH": '"'}]
    matcher = Matcher(matcher.vocab)
    matcher.add("Quote", [pattern])
    doc = Doc(matcher.vocab, words=words)
    assert len(matcher(doc)) == 1


def test_matcher_match_one_plus(matcher):
    control = Matcher(matcher.vocab)
    control.add("BasicPhilippe", [[{"ORTH": "Philippe"}]])
    doc = Doc(control.vocab, words=["Philippe", "Philippe"])
    m = control(doc)
    assert len(m) == 2
    pattern = [{"ORTH": "Philippe"}, {"ORTH": "Philippe", "OP": "+"}]
    matcher.add("KleenePhilippe", [pattern])
    m = matcher(doc)
    assert len(m) == 1


def test_matcher_any_token_operator(en_vocab):
    """Test that patterns with "any token" {} work with operators."""
    matcher = Matcher(en_vocab)
    matcher.add("TEST", [[{"ORTH": "test"}, {"OP": "*"}]])
    doc = Doc(en_vocab, words=["test", "hello", "world"])
    matches = [doc[start:end].text for _, start, end in matcher(doc)]
    assert len(matches) == 3
    assert matches[0] == "test"
    assert matches[1] == "test hello"
    assert matches[2] == "test hello world"


@pytest.mark.usefixtures("clean_underscore")
def test_matcher_extension_attribute(en_vocab):
    matcher = Matcher(en_vocab)
    get_is_fruit = lambda token: token.text in ("apple", "banana")
    Token.set_extension("is_fruit", getter=get_is_fruit, force=True)
    pattern = [{"ORTH": "an"}, {"_": {"is_fruit": True}}]
    matcher.add("HAVING_FRUIT", [pattern])
    doc = Doc(en_vocab, words=["an", "apple"])
    matches = matcher(doc)
    assert len(matches) == 1
    doc = Doc(en_vocab, words=["an", "aardvark"])
    matches = matcher(doc)
    assert len(matches) == 0


def test_matcher_set_value(en_vocab):
    matcher = Matcher(en_vocab)
    pattern = [{"ORTH": {"IN": ["an", "a"]}}]
    matcher.add("A_OR_AN", [pattern])
    doc = Doc(en_vocab, words=["an", "a", "apple"])
    matches = matcher(doc)
    assert len(matches) == 2
    doc = Doc(en_vocab, words=["aardvark"])
    matches = matcher(doc)
    assert len(matches) == 0


def test_matcher_set_value_operator(en_vocab):
    matcher = Matcher(en_vocab)
    pattern = [{"ORTH": {"IN": ["a", "the"]}, "OP": "?"}, {"ORTH": "house"}]
    matcher.add("DET_HOUSE", [pattern])
    doc = Doc(en_vocab, words=["In", "a", "house"])
    matches = matcher(doc)
    assert len(matches) == 2
    doc = Doc(en_vocab, words=["my", "house"])
    matches = matcher(doc)
    assert len(matches) == 1


def test_matcher_regex(en_vocab):
    matcher = Matcher(en_vocab)
    pattern = [{"ORTH": {"REGEX": r"(?:a|an)"}}]
    matcher.add("A_OR_AN", [pattern])
    doc = Doc(en_vocab, words=["an", "a", "hi"])
    matches = matcher(doc)
    assert len(matches) == 2
    doc = Doc(en_vocab, words=["bye"])
    matches = matcher(doc)
    assert len(matches) == 0


def test_matcher_regex_shape(en_vocab):
    matcher = Matcher(en_vocab)
    pattern = [{"SHAPE": {"REGEX": r"^[^x]+$"}}]
    matcher.add("NON_ALPHA", [pattern])
    doc = Doc(en_vocab, words=["99", "problems", "!"])
    matches = matcher(doc)
    assert len(matches) == 2
    doc = Doc(en_vocab, words=["bye"])
    matches = matcher(doc)
    assert len(matches) == 0


@pytest.mark.parametrize(
    "cmp, bad",
    [
        ("==", ["a", "aaa"]),
        ("!=", ["aa"]),
        (">=", ["a"]),
        ("<=", ["aaa"]),
        (">", ["a", "aa"]),
        ("<", ["aa", "aaa"]),
    ],
)
def test_matcher_compare_length(en_vocab, cmp, bad):
    matcher = Matcher(en_vocab)
    pattern = [{"LENGTH": {cmp: 2}}]
    matcher.add("LENGTH_COMPARE", [pattern])
    doc = Doc(en_vocab, words=["a", "aa", "aaa"])
    matches = matcher(doc)
    assert len(matches) == len(doc) - len(bad)
    doc = Doc(en_vocab, words=bad)
    matches = matcher(doc)
    assert len(matches) == 0


def test_matcher_extension_set_membership(en_vocab):
    matcher = Matcher(en_vocab)
    get_reversed = lambda token: "".join(reversed(token.text))
    Token.set_extension("reversed", getter=get_reversed, force=True)
    pattern = [{"_": {"reversed": {"IN": ["eyb", "ih"]}}}]
    matcher.add("REVERSED", [pattern])
    doc = Doc(en_vocab, words=["hi", "bye", "hello"])
    matches = matcher(doc)
    assert len(matches) == 2
    doc = Doc(en_vocab, words=["aardvark"])
    matches = matcher(doc)
    assert len(matches) == 0


def test_matcher_basic_check(en_vocab):
    matcher = Matcher(en_vocab)
    # Potential mistake: pass in pattern instead of list of patterns
    pattern = [{"TEXT": "hello"}, {"TEXT": "world"}]
    with pytest.raises(ValueError):
        matcher.add("TEST", pattern)


def test_attr_pipeline_checks(en_vocab):
    doc1 = Doc(en_vocab, words=["Test"])
    doc1[0].dep_ = "ROOT"
    doc2 = Doc(en_vocab, words=["Test"])
    doc2[0].tag_ = "TAG"
    doc2[0].pos_ = "X"
    doc2[0].morph_ = "Feat=Val"
    doc2[0].lemma_ = "LEMMA"
    doc3 = Doc(en_vocab, words=["Test"])
    # DEP requires DEP
    matcher = Matcher(en_vocab)
    matcher.add("TEST", [[{"DEP": "a"}]])
    matcher(doc1)
    with pytest.raises(ValueError):
        matcher(doc2)
    with pytest.raises(ValueError):
        matcher(doc3)
    # TAG, POS, LEMMA require those values
    for attr in ("TAG", "POS", "LEMMA"):
        matcher = Matcher(en_vocab)
        matcher.add("TEST", [[{attr: "a"}]])
        matcher(doc2)
        with pytest.raises(ValueError):
            matcher(doc1)
        with pytest.raises(ValueError):
            matcher(doc3)
    # TEXT/ORTH only require tokens
    matcher = Matcher(en_vocab)
    matcher.add("TEST", [[{"ORTH": "a"}]])
    matcher(doc1)
    matcher(doc2)
    matcher(doc3)
    matcher = Matcher(en_vocab)
    matcher.add("TEST", [[{"TEXT": "a"}]])
    matcher(doc1)
    matcher(doc2)
    matcher(doc3)


@pytest.mark.parametrize(
    "pattern,text",
    [
        ([{"IS_ALPHA": True}], "a"),
        ([{"IS_ASCII": True}], "a"),
        ([{"IS_DIGIT": True}], "1"),
        ([{"IS_LOWER": True}], "a"),
        ([{"IS_UPPER": True}], "A"),
        ([{"IS_TITLE": True}], "Aaaa"),
        ([{"IS_PUNCT": True}], "."),
        ([{"IS_SPACE": True}], "\n"),
        ([{"IS_BRACKET": True}], "["),
        ([{"IS_QUOTE": True}], '"'),
        ([{"IS_LEFT_PUNCT": True}], "``"),
        ([{"IS_RIGHT_PUNCT": True}], "''"),
        ([{"IS_STOP": True}], "the"),
        ([{"LIKE_NUM": True}], "1"),
        ([{"LIKE_URL": True}], "http://example.com"),
        ([{"LIKE_EMAIL": True}], "mail@example.com"),
    ],
)
def test_matcher_schema_token_attributes(en_vocab, pattern, text):
    matcher = Matcher(en_vocab)
    doc = Doc(en_vocab, words=text.split(" "))
    matcher.add("Rule", [pattern])
    assert len(matcher) == 1
    matches = matcher(doc)
    assert len(matches) == 1


def test_matcher_valid_callback(en_vocab):
    """Test that on_match can only be None or callable."""
    matcher = Matcher(en_vocab)
    with pytest.raises(ValueError):
        matcher.add("TEST", [[{"TEXT": "test"}]], on_match=[])
    matcher(Doc(en_vocab, words=["test"]))


def test_matcher_callback(en_vocab):
    mock = Mock()
    matcher = Matcher(en_vocab)
    pattern = [{"ORTH": "test"}]
    matcher.add("Rule", [pattern], on_match=mock)
    doc = Doc(en_vocab, words=["This", "is", "a", "test", "."])
    matches = matcher(doc)
    mock.assert_called_once_with(matcher, doc, 0, matches)


def test_matcher_span(matcher):
    text = "JavaScript is good but Java is better"
    doc = Doc(matcher.vocab, words=text.split())
    span_js = doc[:3]
    span_java = doc[4:]
    assert len(matcher(doc)) == 2
    assert len(matcher(span_js)) == 1
    assert len(matcher(span_java)) == 1


def test_matcher_as_spans(matcher):
    """Test the new as_spans=True API."""
    text = "JavaScript is good but Java is better"
    doc = Doc(matcher.vocab, words=text.split())
    matches = matcher(doc, as_spans=True)
    assert len(matches) == 2
    assert isinstance(matches[0], Span)
    assert matches[0].text == "JavaScript"
    assert matches[0].label_ == "JS"
    assert isinstance(matches[1], Span)
    assert matches[1].text == "Java"
    assert matches[1].label_ == "Java"


def test_matcher_deprecated(matcher):
    doc = Doc(matcher.vocab, words=["hello", "world"])
    with pytest.warns(DeprecationWarning) as record:
        for _ in matcher.pipe([doc]):
            pass
        assert record.list
        assert "spaCy v3.0" in str(record.list[0].message)
