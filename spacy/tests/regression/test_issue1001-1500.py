# coding: utf-8
from __future__ import unicode_literals

import pytest
import re
from spacy.tokens import Doc
from spacy.vocab import Vocab
from spacy.lang.en import English
from spacy.lang.lex_attrs import LEX_ATTRS
from spacy.matcher import Matcher
from spacy.tokenizer import Tokenizer
from spacy.lemmatizer import Lemmatizer
from spacy.lookups import Lookups
from spacy.symbols import ORTH, LEMMA, POS, VERB, VerbForm_part


def test_issue1061():
    """Test special-case works after tokenizing. Was caching problem."""
    text = "I like _MATH_ even _MATH_ when _MATH_, except when _MATH_ is _MATH_! but not _MATH_."
    tokenizer = English.Defaults.create_tokenizer()
    doc = tokenizer(text)
    assert "MATH" in [w.text for w in doc]
    assert "_MATH_" not in [w.text for w in doc]

    tokenizer.add_special_case("_MATH_", [{ORTH: "_MATH_"}])
    doc = tokenizer(text)
    assert "_MATH_" in [w.text for w in doc]
    assert "MATH" not in [w.text for w in doc]

    # For sanity, check it works when pipeline is clean.
    tokenizer = English.Defaults.create_tokenizer()
    tokenizer.add_special_case("_MATH_", [{ORTH: "_MATH_"}])
    doc = tokenizer(text)
    assert "_MATH_" in [w.text for w in doc]
    assert "MATH" not in [w.text for w in doc]


@pytest.mark.xfail(
    reason="g is split of as a unit, as the suffix regular expression can not look back further (variable-width)"
)
def test_issue1235():
    """Test that g is not split of if preceded by a number and a letter"""
    nlp = English()
    testwords = "e2g 2g 52g"
    doc = nlp(testwords)
    assert len(doc) == 5
    assert doc[0].text == "e2g"
    assert doc[1].text == "2"
    assert doc[2].text == "g"
    assert doc[3].text == "52"
    assert doc[4].text == "g"


def test_issue1242():
    nlp = English()
    doc = nlp("")
    assert len(doc) == 0
    docs = list(nlp.pipe(["", "hello"]))
    assert len(docs[0]) == 0
    assert len(docs[1]) == 1


def test_issue1250():
    """Test cached special cases."""
    special_case = [{ORTH: "reimbur", LEMMA: "reimburse", POS: "VERB"}]
    nlp = English()
    nlp.tokenizer.add_special_case("reimbur", special_case)
    lemmas = [w.lemma_ for w in nlp("reimbur, reimbur...")]
    assert lemmas == ["reimburse", ",", "reimburse", "..."]
    lemmas = [w.lemma_ for w in nlp("reimbur, reimbur...")]
    assert lemmas == ["reimburse", ",", "reimburse", "..."]


def test_issue1257():
    """Test that tokens compare correctly."""
    doc1 = Doc(Vocab(), words=["a", "b", "c"])
    doc2 = Doc(Vocab(), words=["a", "c", "e"])
    assert doc1[0] != doc2[0]
    assert not doc1[0] == doc2[0]


def test_issue1375():
    """Test that token.nbor() raises IndexError for out-of-bounds access."""
    doc = Doc(Vocab(), words=["0", "1", "2"])
    with pytest.raises(IndexError):
        assert doc[0].nbor(-1)
    assert doc[1].nbor(-1).text == "0"
    with pytest.raises(IndexError):
        assert doc[2].nbor(1)
    assert doc[1].nbor(1).text == "2"


def test_issue1387():
    tag_map = {"VBG": {POS: VERB, VerbForm_part: True}}
    lookups = Lookups()
    lookups.add_table("lemma_index", {"verb": ("cope", "cop")})
    lookups.add_table("lemma_exc", {"verb": {"coping": ("cope",)}})
    lookups.add_table("lemma_rules", {"verb": [["ing", ""]]})
    lemmatizer = Lemmatizer(lookups)
    vocab = Vocab(lemmatizer=lemmatizer, tag_map=tag_map)
    doc = Doc(vocab, words=["coping"])
    doc[0].tag_ = "VBG"
    assert doc[0].text == "coping"
    assert doc[0].lemma_ == "cope"


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


def test_issue1488():
    prefix_re = re.compile(r"""[\[\("']""")
    suffix_re = re.compile(r"""[\]\)"']""")
    infix_re = re.compile(r"""[-~\.]""")
    simple_url_re = re.compile(r"""^https?://""")

    def my_tokenizer(nlp):
        return Tokenizer(
            nlp.vocab,
            {},
            prefix_search=prefix_re.search,
            suffix_search=suffix_re.search,
            infix_finditer=infix_re.finditer,
            token_match=simple_url_re.match,
        )

    nlp = English()
    nlp.tokenizer = my_tokenizer(nlp)
    doc = nlp("This is a test.")
    for token in doc:
        assert token.text


def test_issue1494():
    infix_re = re.compile(r"""[^a-z]""")
    test_cases = [
        ("token 123test", ["token", "1", "2", "3", "test"]),
        ("token 1test", ["token", "1test"]),
        ("hello...test", ["hello", ".", ".", ".", "test"]),
    ]

    def new_tokenizer(nlp):
        return Tokenizer(nlp.vocab, {}, infix_finditer=infix_re.finditer)

    nlp = English()
    nlp.tokenizer = new_tokenizer(nlp)
    for text, expected in test_cases:
        assert [token.text for token in nlp(text)] == expected
