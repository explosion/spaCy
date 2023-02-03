import re

import pytest

from spacy.attrs import IS_PUNCT, LOWER, ORTH
from spacy.errors import MatchPatternError
from spacy.lang.en import English
from spacy.lang.lex_attrs import LEX_ATTRS
from spacy.matcher import Matcher
from spacy.tokens import Doc, Span, Token
from spacy.vocab import Vocab

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


@pytest.mark.issue(118)
@pytest.mark.parametrize(
    "patterns",
    [
        [[{"LOWER": "celtics"}], [{"LOWER": "boston"}, {"LOWER": "celtics"}]],
        [[{"LOWER": "boston"}, {"LOWER": "celtics"}], [{"LOWER": "celtics"}]],
    ],
)
def test_issue118(en_tokenizer, patterns):
    """Test a bug that arose from having overlapping matches"""
    text = (
        "how many points did lebron james score against the boston celtics last night"
    )
    doc = en_tokenizer(text)
    ORG = doc.vocab.strings["ORG"]
    matcher = Matcher(doc.vocab)
    matcher.add("BostonCeltics", patterns)
    assert len(list(doc.ents)) == 0
    matches = [(ORG, start, end) for _, start, end in matcher(doc)]
    assert matches == [(ORG, 9, 11), (ORG, 10, 11)]
    doc.ents = matches[:1]
    ents = list(doc.ents)
    assert len(ents) == 1
    assert ents[0].label == ORG
    assert ents[0].start == 9
    assert ents[0].end == 11


@pytest.mark.issue(118)
@pytest.mark.parametrize(
    "patterns",
    [
        [[{"LOWER": "boston"}], [{"LOWER": "boston"}, {"LOWER": "celtics"}]],
        [[{"LOWER": "boston"}, {"LOWER": "celtics"}], [{"LOWER": "boston"}]],
    ],
)
def test_issue118_prefix_reorder(en_tokenizer, patterns):
    """Test a bug that arose from having overlapping matches"""
    text = (
        "how many points did lebron james score against the boston celtics last night"
    )
    doc = en_tokenizer(text)
    ORG = doc.vocab.strings["ORG"]
    matcher = Matcher(doc.vocab)
    matcher.add("BostonCeltics", patterns)
    assert len(list(doc.ents)) == 0
    matches = [(ORG, start, end) for _, start, end in matcher(doc)]
    doc.ents += tuple(matches)[1:]
    assert matches == [(ORG, 9, 10), (ORG, 9, 11)]
    ents = doc.ents
    assert len(ents) == 1
    assert ents[0].label == ORG
    assert ents[0].start == 9
    assert ents[0].end == 11


@pytest.mark.issue(242)
def test_issue242(en_tokenizer):
    """Test overlapping multi-word phrases."""
    text = "There are different food safety standards in different countries."
    patterns = [
        [{"LOWER": "food"}, {"LOWER": "safety"}],
        [{"LOWER": "safety"}, {"LOWER": "standards"}],
    ]
    doc = en_tokenizer(text)
    matcher = Matcher(doc.vocab)
    matcher.add("FOOD", patterns)
    matches = [(ent_type, start, end) for ent_type, start, end in matcher(doc)]
    match1, match2 = matches
    assert match1[1] == 3
    assert match1[2] == 5
    assert match2[1] == 4
    assert match2[2] == 6
    with pytest.raises(ValueError):
        # One token can only be part of one entity, so test that the matches
        # can't be added as entities
        doc.ents += tuple(matches)


@pytest.mark.issue(587)
def test_issue587(en_tokenizer):
    """Test that Matcher doesn't segfault on particular input"""
    doc = en_tokenizer("a b; c")
    matcher = Matcher(doc.vocab)
    matcher.add("TEST1", [[{ORTH: "a"}, {ORTH: "b"}]])
    matches = matcher(doc)
    assert len(matches) == 1
    matcher.add("TEST2", [[{ORTH: "a"}, {ORTH: "b"}, {IS_PUNCT: True}, {ORTH: "c"}]])
    matches = matcher(doc)
    assert len(matches) == 2
    matcher.add("TEST3", [[{ORTH: "a"}, {ORTH: "b"}, {IS_PUNCT: True}, {ORTH: "d"}]])
    matches = matcher(doc)
    assert len(matches) == 2


@pytest.mark.issue(588)
def test_issue588(en_vocab):
    """Test if empty specs still cause an error when adding patterns"""
    matcher = Matcher(en_vocab)
    with pytest.raises(ValueError):
        matcher.add("TEST", [[]])


@pytest.mark.issue(590)
def test_issue590(en_vocab):
    """Test overlapping matches"""
    doc = Doc(en_vocab, words=["n", "=", "1", ";", "a", ":", "5", "%"])
    matcher = Matcher(en_vocab)
    matcher.add(
        "ab", [[{"IS_ALPHA": True}, {"ORTH": ":"}, {"LIKE_NUM": True}, {"ORTH": "%"}]]
    )
    matcher.add("ab", [[{"IS_ALPHA": True}, {"ORTH": "="}, {"LIKE_NUM": True}]])
    matches = matcher(doc)
    assert len(matches) == 2


@pytest.mark.issue(615)
def test_issue615(en_tokenizer):
    def merge_phrases(matcher, doc, i, matches):
        """Merge a phrase. We have to be careful here because we'll change the
        token indices. To avoid problems, merge all the phrases once we're called
        on the last match."""
        if i != len(matches) - 1:
            return None
        spans = [Span(doc, start, end, label=label) for label, start, end in matches]
        with doc.retokenize() as retokenizer:
            for span in spans:
                tag = "NNP" if span.label_ else span.root.tag_
                attrs = {"tag": tag, "lemma": span.text}
                retokenizer.merge(span, attrs=attrs)
                doc.ents = doc.ents + (span,)

    text = "The golf club is broken"
    pattern = [{"ORTH": "golf"}, {"ORTH": "club"}]
    label = "Sport_Equipment"
    doc = en_tokenizer(text)
    matcher = Matcher(doc.vocab)
    matcher.add(label, [pattern], on_match=merge_phrases)
    matcher(doc)
    entities = list(doc.ents)
    assert entities != []
    assert entities[0].label != 0


@pytest.mark.issue(850)
def test_issue850():
    """The variable-length pattern matches the succeeding token. Check we
    handle the ambiguity correctly."""
    vocab = Vocab(lex_attr_getters={LOWER: lambda string: string.lower()})
    matcher = Matcher(vocab)
    pattern = [{"LOWER": "bob"}, {"OP": "*"}, {"LOWER": "frank"}]
    matcher.add("FarAway", [pattern])
    doc = Doc(matcher.vocab, words=["bob", "and", "and", "frank"])
    match = matcher(doc)
    assert len(match) == 1
    ent_id, start, end = match[0]
    assert start == 0
    assert end == 4


@pytest.mark.issue(850)
def test_issue850_basic():
    """Test Matcher matches with '*' operator and Boolean flag"""
    vocab = Vocab(lex_attr_getters={LOWER: lambda string: string.lower()})
    matcher = Matcher(vocab)
    pattern = [{"LOWER": "bob"}, {"OP": "*", "LOWER": "and"}, {"LOWER": "frank"}]
    matcher.add("FarAway", [pattern])
    doc = Doc(matcher.vocab, words=["bob", "and", "and", "frank"])
    match = matcher(doc)
    assert len(match) == 1
    ent_id, start, end = match[0]
    assert start == 0
    assert end == 4


@pytest.mark.issue(1434)
def test_issue1434():
    """Test matches occur when optional element at end of short doc."""
    pattern = [{"ORTH": "Hello"}, {"IS_ALPHA": True, "OP": "?"}]
    vocab = Vocab(lex_attr_getters=LEX_ATTRS)
    hello_world = Doc(vocab, words=["Hello", "World"])
    hello = Doc(vocab, words=["Hello"])
    matcher = Matcher(vocab)
    matcher.add("MyMatcher", [pattern])
    matches = matcher(hello_world)
    assert matches
    matches = matcher(hello)
    assert matches


@pytest.mark.parametrize(
    "string,start,end",
    [
        ("a", 0, 1),
        ("a b", 0, 2),
        ("a c", 0, 1),
        ("a b c", 0, 2),
        ("a b b c", 0, 3),
        ("a b b", 0, 3),
    ],
)
@pytest.mark.issue(1450)
def test_issue1450(string, start, end):
    """Test matcher works when patterns end with * operator."""
    pattern = [{"ORTH": "a"}, {"ORTH": "b", "OP": "*"}]
    matcher = Matcher(Vocab())
    matcher.add("TSTEND", [pattern])
    doc = Doc(Vocab(), words=string.split())
    matches = matcher(doc)
    if start is None or end is None:
        assert matches == []
    assert matches[-1][1] == start
    assert matches[-1][2] == end


@pytest.mark.issue(1945)
def test_issue1945():
    """Test regression in Matcher introduced in v2.0.6."""
    matcher = Matcher(Vocab())
    matcher.add("MWE", [[{"orth": "a"}, {"orth": "a"}]])
    doc = Doc(matcher.vocab, words=["a", "a", "a"])
    matches = matcher(doc)  # we should see two overlapping matches here
    assert len(matches) == 2
    assert matches[0][1:] == (0, 2)
    assert matches[1][1:] == (1, 3)


@pytest.mark.issue(1971)
def test_issue1971(en_vocab):
    # Possibly related to #2675 and #2671?
    matcher = Matcher(en_vocab)
    pattern = [
        {"ORTH": "Doe"},
        {"ORTH": "!", "OP": "?"},
        {"_": {"optional": True}, "OP": "?"},
        {"ORTH": "!", "OP": "?"},
    ]
    Token.set_extension("optional", default=False)
    matcher.add("TEST", [pattern])
    doc = Doc(en_vocab, words=["Hello", "John", "Doe", "!"])
    # We could also assert length 1 here, but this is more conclusive, because
    # the real problem here is that it returns a duplicate match for a match_id
    # that's not actually in the vocab!
    matches = matcher(doc)
    assert all([match_id in en_vocab.strings for match_id, start, end in matches])


@pytest.mark.issue(1971)
def test_issue_1971_2(en_vocab):
    matcher = Matcher(en_vocab)
    pattern1 = [{"ORTH": "EUR", "LOWER": {"IN": ["eur"]}}, {"LIKE_NUM": True}]
    pattern2 = [{"LIKE_NUM": True}, {"ORTH": "EUR"}]  # {"IN": ["EUR"]}}]
    doc = Doc(en_vocab, words=["EUR", "10", "is", "10", "EUR"])
    matcher.add("TEST1", [pattern1, pattern2])
    matches = matcher(doc)
    assert len(matches) == 2


@pytest.mark.issue(1971)
def test_issue_1971_3(en_vocab):
    """Test that pattern matches correctly for multiple extension attributes."""
    Token.set_extension("a", default=1, force=True)
    Token.set_extension("b", default=2, force=True)
    doc = Doc(en_vocab, words=["hello", "world"])
    matcher = Matcher(en_vocab)
    matcher.add("A", [[{"_": {"a": 1}}]])
    matcher.add("B", [[{"_": {"b": 2}}]])
    matches = sorted((en_vocab.strings[m_id], s, e) for m_id, s, e in matcher(doc))
    assert len(matches) == 4
    assert matches == sorted([("A", 0, 1), ("A", 1, 2), ("B", 0, 1), ("B", 1, 2)])


@pytest.mark.issue(1971)
def test_issue_1971_4(en_vocab):
    """Test that pattern matches correctly with multiple extension attribute
    values on a single token.
    """
    Token.set_extension("ext_a", default="str_a", force=True)
    Token.set_extension("ext_b", default="str_b", force=True)
    matcher = Matcher(en_vocab)
    doc = Doc(en_vocab, words=["this", "is", "text"])
    pattern = [{"_": {"ext_a": "str_a", "ext_b": "str_b"}}] * 3
    matcher.add("TEST", [pattern])
    matches = matcher(doc)
    # Uncommenting this caused a segmentation fault
    assert len(matches) == 1
    assert matches[0] == (en_vocab.strings["TEST"], 0, 3)


@pytest.mark.issue(2464)
def test_issue2464(en_vocab):
    """Test problem with successive ?. This is the same bug, so putting it here."""
    matcher = Matcher(en_vocab)
    doc = Doc(en_vocab, words=["a", "b"])
    matcher.add("4", [[{"OP": "?"}, {"OP": "?"}]])
    matches = matcher(doc)
    assert len(matches) == 3


@pytest.mark.issue(2569)
def test_issue2569(en_tokenizer):
    """Test that operator + is greedy."""
    doc = en_tokenizer("It is May 15, 1993.")
    doc.ents = [Span(doc, 2, 6, label=doc.vocab.strings["DATE"])]
    matcher = Matcher(doc.vocab)
    matcher.add("RULE", [[{"ENT_TYPE": "DATE", "OP": "+"}]])
    matched = [doc[start:end] for _, start, end in matcher(doc)]
    matched = sorted(matched, key=len, reverse=True)
    assert len(matched) == 10
    assert len(matched[0]) == 4
    assert matched[0].text == "May 15, 1993"


@pytest.mark.issue(2671)
def test_issue2671():
    """Ensure the correct entity ID is returned for matches with quantifiers.
    See also #2675
    """
    nlp = English()
    matcher = Matcher(nlp.vocab)
    pattern_id = "test_pattern"
    pattern = [
        {"LOWER": "high"},
        {"IS_PUNCT": True, "OP": "?"},
        {"LOWER": "adrenaline"},
    ]
    matcher.add(pattern_id, [pattern])
    doc1 = nlp("This is a high-adrenaline situation.")
    doc2 = nlp("This is a high adrenaline situation.")
    matches1 = matcher(doc1)
    for match_id, start, end in matches1:
        assert nlp.vocab.strings[match_id] == pattern_id
    matches2 = matcher(doc2)
    for match_id, start, end in matches2:
        assert nlp.vocab.strings[match_id] == pattern_id


@pytest.mark.issue(3009)
def test_issue3009(en_vocab):
    """Test problem with matcher quantifiers"""
    patterns = [
        [{"ORTH": "has"}, {"LOWER": "to"}, {"LOWER": "do"}, {"TAG": "IN"}],
        [
            {"ORTH": "has"},
            {"IS_ASCII": True, "IS_PUNCT": False, "OP": "*"},
            {"LOWER": "to"},
            {"LOWER": "do"},
            {"TAG": "IN"},
        ],
        [
            {"ORTH": "has"},
            {"IS_ASCII": True, "IS_PUNCT": False, "OP": "?"},
            {"LOWER": "to"},
            {"LOWER": "do"},
            {"TAG": "IN"},
        ],
    ]
    words = ["also", "has", "to", "do", "with"]
    tags = ["RB", "VBZ", "TO", "VB", "IN"]
    pos = ["ADV", "VERB", "ADP", "VERB", "ADP"]
    doc = Doc(en_vocab, words=words, tags=tags, pos=pos)
    matcher = Matcher(en_vocab)
    for i, pattern in enumerate(patterns):
        matcher.add(str(i), [pattern])
        matches = matcher(doc)
        assert matches


@pytest.mark.issue(3328)
def test_issue3328(en_vocab):
    doc = Doc(en_vocab, words=["Hello", ",", "how", "are", "you", "doing", "?"])
    matcher = Matcher(en_vocab)
    patterns = [
        [{"LOWER": {"IN": ["hello", "how"]}}],
        [{"LOWER": {"IN": ["you", "doing"]}}],
    ]
    matcher.add("TEST", patterns)
    matches = matcher(doc)
    assert len(matches) == 4
    matched_texts = [doc[start:end].text for _, start, end in matches]
    assert matched_texts == ["Hello", "how", "you", "doing"]


@pytest.mark.issue(3549)
def test_issue3549(en_vocab):
    """Test that match pattern validation doesn't raise on empty errors."""
    matcher = Matcher(en_vocab, validate=True)
    pattern = [{"LOWER": "hello"}, {"LOWER": "world"}]
    matcher.add("GOOD", [pattern])
    with pytest.raises(MatchPatternError):
        matcher.add("BAD", [[{"X": "Y"}]])


@pytest.mark.skip("Matching currently only works on strings and integers")
@pytest.mark.issue(3555)
def test_issue3555(en_vocab):
    """Test that custom extensions with default None don't break matcher."""
    Token.set_extension("issue3555", default=None)
    matcher = Matcher(en_vocab)
    pattern = [{"ORTH": "have"}, {"_": {"issue3555": True}}]
    matcher.add("TEST", [pattern])
    doc = Doc(en_vocab, words=["have", "apple"])
    matcher(doc)


@pytest.mark.issue(3839)
def test_issue3839(en_vocab):
    """Test that match IDs returned by the matcher are correct, are in the string"""
    doc = Doc(en_vocab, words=["terrific", "group", "of", "people"])
    matcher = Matcher(en_vocab)
    match_id = "PATTERN"
    pattern1 = [{"LOWER": "terrific"}, {"OP": "?"}, {"LOWER": "group"}]
    pattern2 = [{"LOWER": "terrific"}, {"OP": "?"}, {"OP": "?"}, {"LOWER": "group"}]
    matcher.add(match_id, [pattern1])
    matches = matcher(doc)
    assert matches[0][0] == en_vocab.strings[match_id]
    matcher = Matcher(en_vocab)
    matcher.add(match_id, [pattern2])
    matches = matcher(doc)
    assert matches[0][0] == en_vocab.strings[match_id]


@pytest.mark.issue(3879)
def test_issue3879(en_vocab):
    doc = Doc(en_vocab, words=["This", "is", "a", "test", "."])
    assert len(doc) == 5
    pattern = [{"ORTH": "This", "OP": "?"}, {"OP": "?"}, {"ORTH": "test"}]
    matcher = Matcher(en_vocab)
    matcher.add("TEST", [pattern])
    assert len(matcher(doc)) == 2  # fails because of a FP match 'is a test'


@pytest.mark.issue(3951)
def test_issue3951(en_vocab):
    """Test that combinations of optional rules are matched correctly."""
    matcher = Matcher(en_vocab)
    pattern = [
        {"LOWER": "hello"},
        {"LOWER": "this", "OP": "?"},
        {"OP": "?"},
        {"LOWER": "world"},
    ]
    matcher.add("TEST", [pattern])
    doc = Doc(en_vocab, words=["Hello", "my", "new", "world"])
    matches = matcher(doc)
    assert len(matches) == 0


@pytest.mark.issue(4120)
def test_issue4120(en_vocab):
    """Test that matches without a final {OP: ?} token are returned."""
    matcher = Matcher(en_vocab)
    matcher.add("TEST", [[{"ORTH": "a"}, {"OP": "?"}]])
    doc1 = Doc(en_vocab, words=["a"])
    assert len(matcher(doc1)) == 1  # works
    doc2 = Doc(en_vocab, words=["a", "b", "c"])
    assert len(matcher(doc2)) == 2  # fixed
    matcher = Matcher(en_vocab)
    matcher.add("TEST", [[{"ORTH": "a"}, {"OP": "?"}, {"ORTH": "b"}]])
    doc3 = Doc(en_vocab, words=["a", "b", "b", "c"])
    assert len(matcher(doc3)) == 2  # works
    matcher = Matcher(en_vocab)
    matcher.add("TEST", [[{"ORTH": "a"}, {"OP": "?"}, {"ORTH": "b", "OP": "?"}]])
    doc4 = Doc(en_vocab, words=["a", "b", "b", "c"])
    assert len(matcher(doc4)) == 3  # fixed


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
    for key, s, e in matches:
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


@pytest.mark.issue(1450)
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
        ("aaab", "a{2,} b", [0, 0, 0, 1]),
        ("aaab", "a{,3} b", [0, 0, 0, 1]),
        ("aaab", "a{2} b", [0, 0, 1]),
        ("aaab", "a{2,3} b", [0, 0, 0, 1]),
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
            elif part.endswith("}"):
                pattern.append({"ORTH": part[0], "OP": part[1:]})
            else:
                pattern.append({"ORTH": part})
        matcher.add("PATTERN", [pattern], greedy="LONGEST")
        matches = matcher(doc, with_alignments=True)
        n_matches = len(matches)

        _, s, e, expected = matches[0]

        assert expected == result, (string, pattern_str, s, e, n_matches)


def test_matcher_with_alignments_non_greedy(en_vocab):
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
        (18, "aaab", "a{2,} b", [[0, 0, 1], [0, 0, 0, 1]]),
        (19, "aaab", "a{3} b", [[0, 0, 0, 1]]),
        (20, "aaab", "a{2} b", [[0, 0, 1]]),
        (21, "aaab", "a{2,3} b", [[0, 0, 1], [0, 0, 0, 1]]),
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
            elif part.endswith("}"):
                pattern.append({"ORTH": part[0], "OP": part[1:]})
            else:
                pattern.append({"ORTH": part})

        matcher.add("PATTERN", [pattern])
        matches = matcher(doc, with_alignments=True)
        n_matches = len(matches)

        for _, s, e, expected in matches:
            assert expected in results, (case_id, string, pattern_str, s, e, n_matches)
            assert len(expected) == e - s
