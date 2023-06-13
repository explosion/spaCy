import re

import numpy
import pytest

from spacy.lang.de import German
from spacy.lang.en import English
from spacy.symbols import ORTH
from spacy.tokenizer import Tokenizer
from spacy.tokens import Doc
from spacy.training import Example
from spacy.util import (
    compile_infix_regex,
    compile_prefix_regex,
    compile_suffix_regex,
    ensure_path,
)
from spacy.vocab import Vocab


@pytest.mark.issue(743)
def test_issue743():
    doc = Doc(Vocab(), ["hello", "world"])
    token = doc[0]
    s = set([token])
    items = list(s)
    assert items[0] is token


@pytest.mark.issue(801)
@pytest.mark.skip(
    reason="Can not be fixed unless with variable-width lookbehinds, cf. PR #3218"
)
@pytest.mark.parametrize(
    "text,tokens",
    [
        ('"deserve,"--and', ['"', "deserve", ',"--', "and"]),
        ("exception;--exclusive", ["exception", ";--", "exclusive"]),
        ("day.--Is", ["day", ".--", "Is"]),
        ("refinement:--just", ["refinement", ":--", "just"]),
        ("memories?--To", ["memories", "?--", "To"]),
        ("Useful.=--Therefore", ["Useful", ".=--", "Therefore"]),
        ("=Hope.=--Pandora", ["=", "Hope", ".=--", "Pandora"]),
    ],
)
def test_issue801(en_tokenizer, text, tokens):
    """Test that special characters + hyphens are split correctly."""
    doc = en_tokenizer(text)
    assert len(doc) == len(tokens)
    assert [t.text for t in doc] == tokens


@pytest.mark.issue(1061)
def test_issue1061():
    """Test special-case works after tokenizing. Was caching problem."""
    text = "I like _MATH_ even _MATH_ when _MATH_, except when _MATH_ is _MATH_! but not _MATH_."
    tokenizer = English().tokenizer
    doc = tokenizer(text)
    assert "MATH" in [w.text for w in doc]
    assert "_MATH_" not in [w.text for w in doc]

    tokenizer.add_special_case("_MATH_", [{ORTH: "_MATH_"}])
    doc = tokenizer(text)
    assert "_MATH_" in [w.text for w in doc]
    assert "MATH" not in [w.text for w in doc]

    # For sanity, check it works when pipeline is clean.
    tokenizer = English().tokenizer
    tokenizer.add_special_case("_MATH_", [{ORTH: "_MATH_"}])
    doc = tokenizer(text)
    assert "_MATH_" in [w.text for w in doc]
    assert "MATH" not in [w.text for w in doc]


@pytest.mark.issue(1963)
def test_issue1963(en_tokenizer):
    """Test that doc.merge() resizes doc.tensor"""
    doc = en_tokenizer("a b c d")
    doc.tensor = numpy.ones((len(doc), 128), dtype="f")
    with doc.retokenize() as retokenizer:
        retokenizer.merge(doc[0:2])
    assert len(doc) == 3
    assert doc.tensor.shape == (3, 128)


@pytest.mark.skip(
    reason="Can not be fixed without variable-width look-behind (which we don't want)"
)
@pytest.mark.issue(1235)
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


@pytest.mark.issue(1242)
def test_issue1242():
    nlp = English()
    doc = nlp("")
    assert len(doc) == 0
    docs = list(nlp.pipe(["", "hello"]))
    assert len(docs[0]) == 0
    assert len(docs[1]) == 1


@pytest.mark.issue(1257)
def test_issue1257():
    """Test that tokens compare correctly."""
    doc1 = Doc(Vocab(), words=["a", "b", "c"])
    doc2 = Doc(Vocab(), words=["a", "c", "e"])
    assert doc1[0] != doc2[0]
    assert not doc1[0] == doc2[0]


@pytest.mark.issue(1375)
def test_issue1375():
    """Test that token.nbor() raises IndexError for out-of-bounds access."""
    doc = Doc(Vocab(), words=["0", "1", "2"])
    with pytest.raises(IndexError):
        assert doc[0].nbor(-1)
    assert doc[1].nbor(-1).text == "0"
    with pytest.raises(IndexError):
        assert doc[2].nbor(1)
    assert doc[1].nbor(1).text == "2"


@pytest.mark.issue(1488)
def test_issue1488():
    """Test that tokenizer can parse DOT inside non-whitespace separators"""
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


@pytest.mark.issue(1494)
def test_issue1494():
    """Test if infix_finditer works correctly"""
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


@pytest.mark.skip(
    reason="Can not be fixed without iterative looping between prefix/suffix and infix"
)
@pytest.mark.issue(2070)
def test_issue2070():
    """Test that checks that a dot followed by a quote is handled
    appropriately.
    """
    # Problem: The dot is now properly split off, but the prefix/suffix rules
    # are not applied again afterwards. This means that the quote will still be
    # attached to the remaining token.
    nlp = English()
    doc = nlp('First sentence."A quoted sentence" he said ...')
    assert len(doc) == 11


@pytest.mark.issue(2926)
def test_issue2926(fr_tokenizer):
    """Test that the tokenizer correctly splits tokens separated by a slash (/)
    ending in a digit.
    """
    doc = fr_tokenizer("Learn html5/css3/javascript/jquery")
    assert len(doc) == 8
    assert doc[0].text == "Learn"
    assert doc[1].text == "html5"
    assert doc[2].text == "/"
    assert doc[3].text == "css3"
    assert doc[4].text == "/"
    assert doc[5].text == "javascript"
    assert doc[6].text == "/"
    assert doc[7].text == "jquery"


@pytest.mark.parametrize(
    "text",
    [
        "ABLEItemColumn IAcceptance Limits of ErrorIn-Service Limits of ErrorColumn IIColumn IIIColumn IVColumn VComputed VolumeUnder Registration of\xa0VolumeOver Registration of\xa0VolumeUnder Registration of\xa0VolumeOver Registration of\xa0VolumeCubic FeetCubic FeetCubic FeetCubic FeetCubic Feet1Up to 10.0100.0050.0100.005220.0200.0100.0200.010350.0360.0180.0360.0184100.0500.0250.0500.0255Over 100.5% of computed volume0.25% of computed volume0.5% of computed volume0.25% of computed volume TABLE ItemColumn IAcceptance Limits of ErrorIn-Service Limits of ErrorColumn IIColumn IIIColumn IVColumn VComputed VolumeUnder Registration of\xa0VolumeOver Registration of\xa0VolumeUnder Registration of\xa0VolumeOver Registration of\xa0VolumeCubic FeetCubic FeetCubic FeetCubic FeetCubic Feet1Up to 10.0100.0050.0100.005220.0200.0100.0200.010350.0360.0180.0360.0184100.0500.0250.0500.0255Over 100.5% of computed volume0.25% of computed volume0.5% of computed volume0.25% of computed volume ItemColumn IAcceptance Limits of ErrorIn-Service Limits of ErrorColumn IIColumn IIIColumn IVColumn VComputed VolumeUnder Registration of\xa0VolumeOver Registration of\xa0VolumeUnder Registration of\xa0VolumeOver Registration of\xa0VolumeCubic FeetCubic FeetCubic FeetCubic FeetCubic Feet1Up to 10.0100.0050.0100.005220.0200.0100.0200.010350.0360.0180.0360.0184100.0500.0250.0500.0255Over 100.5% of computed volume0.25% of computed volume0.5% of computed volume0.25% of computed volume",
        "oow.jspsearch.eventoracleopenworldsearch.technologyoraclesolarissearch.technologystoragesearch.technologylinuxsearch.technologyserverssearch.technologyvirtualizationsearch.technologyengineeredsystemspcodewwmkmppscem:",
    ],
)
@pytest.mark.issue(2626)
def test_issue2626_2835(en_tokenizer, text):
    """Check that sentence doesn't cause an infinite loop in the tokenizer."""
    doc = en_tokenizer(text)
    assert doc


@pytest.mark.issue(2656)
def test_issue2656(en_tokenizer):
    """Test that tokenizer correctly splits off punctuation after numbers with
    decimal points.
    """
    doc = en_tokenizer("I went for 40.3, and got home by 10.0.")
    assert len(doc) == 11
    assert doc[0].text == "I"
    assert doc[1].text == "went"
    assert doc[2].text == "for"
    assert doc[3].text == "40.3"
    assert doc[4].text == ","
    assert doc[5].text == "and"
    assert doc[6].text == "got"
    assert doc[7].text == "home"
    assert doc[8].text == "by"
    assert doc[9].text == "10.0"
    assert doc[10].text == "."


@pytest.mark.issue(2754)
def test_issue2754(en_tokenizer):
    """Test that words like 'a' and 'a.m.' don't get exceptional norm values."""
    a = en_tokenizer("a")
    assert a[0].norm_ == "a"
    am = en_tokenizer("am")
    assert am[0].norm_ == "am"


@pytest.mark.issue(3002)
def test_issue3002():
    """Test that the tokenizer doesn't hang on a long list of dots"""
    nlp = German()
    doc = nlp(
        "880.794.982.218.444.893.023.439.794.626.120.190.780.624.990.275.671 ist eine lange Zahl"
    )
    assert len(doc) == 5


@pytest.mark.skip(reason="default suffix rules avoid one upper-case letter before dot")
@pytest.mark.issue(3449)
def test_issue3449():
    nlp = English()
    nlp.add_pipe("sentencizer")
    text1 = "He gave the ball to I. Do you want to go to the movies with I?"
    text2 = "He gave the ball to I.  Do you want to go to the movies with I?"
    text3 = "He gave the ball to I.\nDo you want to go to the movies with I?"
    t1 = nlp(text1)
    t2 = nlp(text2)
    t3 = nlp(text3)
    assert t1[5].text == "I"
    assert t2[5].text == "I"
    assert t3[5].text == "I"


@pytest.mark.parametrize(
    "text,words", [("A'B C", ["A", "'", "B", "C"]), ("A-B", ["A-B"])]
)
def test_gold_misaligned(en_tokenizer, text, words):
    doc = en_tokenizer(text)
    Example.from_dict(doc, {"words": words})


def test_tokenizer_handles_no_word(tokenizer):
    tokens = tokenizer("")
    assert len(tokens) == 0


@pytest.mark.parametrize("text", ["lorem"])
def test_tokenizer_handles_single_word(tokenizer, text):
    tokens = tokenizer(text)
    assert tokens[0].text == text


def test_tokenizer_handles_punct(tokenizer):
    text = "Lorem, ipsum."
    tokens = tokenizer(text)
    assert len(tokens) == 4
    assert tokens[0].text == "Lorem"
    assert tokens[1].text == ","
    assert tokens[2].text == "ipsum"
    assert tokens[1].text != "Lorem"


def test_tokenizer_handles_punct_braces(tokenizer):
    text = "Lorem, (ipsum)."
    tokens = tokenizer(text)
    assert len(tokens) == 6


def test_tokenizer_handles_digits(tokenizer):
    exceptions = ["hu", "bn"]
    text = "Lorem ipsum: 1984."
    tokens = tokenizer(text)

    if tokens[0].lang_ not in exceptions:
        assert len(tokens) == 5
        assert tokens[0].text == "Lorem"
        assert tokens[3].text == "1984"


@pytest.mark.parametrize(
    "text",
    ["google.com", "python.org", "spacy.io", "explosion.ai", "http://www.google.com"],
)
def test_tokenizer_keep_urls(tokenizer, text):
    tokens = tokenizer(text)
    assert len(tokens) == 1


@pytest.mark.parametrize("text", ["NASDAQ:GOOG"])
def test_tokenizer_colons(tokenizer, text):
    tokens = tokenizer(text)
    assert len(tokens) == 3


@pytest.mark.parametrize(
    "text", ["hello123@example.com", "hi+there@gmail.it", "matt@explosion.ai"]
)
def test_tokenizer_keeps_email(tokenizer, text):
    tokens = tokenizer(text)
    assert len(tokens) == 1


def test_tokenizer_handles_long_text(tokenizer):
    text = """Lorem ipsum dolor sit amet, consectetur adipiscing elit

Cras egestas orci non porttitor maximus.
Maecenas quis odio id dolor rhoncus dignissim. Curabitur sed velit at orci ultrices sagittis. Nulla commodo euismod arcu eget vulputate.

Phasellus tincidunt, augue quis porta finibus, massa sapien consectetur augue, non lacinia enim nibh eget ipsum. Vestibulum in bibendum mauris.

"Nullam porta fringilla enim, a dictum orci consequat in." Mauris nec malesuada justo."""

    tokens = tokenizer(text)
    assert len(tokens) > 5


@pytest.mark.parametrize("file_name", ["sun.txt"])
def test_tokenizer_handle_text_from_file(tokenizer, file_name):
    loc = ensure_path(__file__).parent / file_name
    with loc.open("r", encoding="utf8") as infile:
        text = infile.read()
    assert len(text) != 0
    tokens = tokenizer(text)
    assert len(tokens) > 100


def test_tokenizer_suspected_freeing_strings(tokenizer):
    text1 = "Lorem dolor sit amet, consectetur adipiscing elit."
    text2 = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    tokens1 = tokenizer(text1)
    tokens2 = tokenizer(text2)
    assert tokens1[0].text == "Lorem"
    assert tokens2[0].text == "Lorem"


@pytest.mark.parametrize("text,tokens", [("lorem", [{"orth": "lo"}, {"orth": "rem"}])])
def test_tokenizer_add_special_case(tokenizer, text, tokens):
    tokenizer.add_special_case(text, tokens)
    doc = tokenizer(text)
    assert doc[0].text == tokens[0]["orth"]
    assert doc[1].text == tokens[1]["orth"]


@pytest.mark.parametrize(
    "text,tokens",
    [
        ("lorem", [{"orth": "lo"}, {"orth": "re"}]),
        ("lorem", [{"orth": "lo", "tag": "A"}, {"orth": "rem"}]),
    ],
)
def test_tokenizer_validate_special_case(tokenizer, text, tokens):
    with pytest.raises(ValueError):
        tokenizer.add_special_case(text, tokens)


@pytest.mark.parametrize(
    "text,tokens", [("lorem", [{"orth": "lo", "norm": "LO"}, {"orth": "rem"}])]
)
def test_tokenizer_add_special_case_tag(text, tokens):
    vocab = Vocab()
    tokenizer = Tokenizer(vocab, {}, None, None, None)
    tokenizer.add_special_case(text, tokens)
    doc = tokenizer(text)
    assert doc[0].text == tokens[0]["orth"]
    assert doc[0].norm_ == tokens[0]["norm"]
    assert doc[1].text == tokens[1]["orth"]


def test_tokenizer_special_cases_with_affixes(tokenizer):
    text = '(((_SPECIAL_ A/B, A/B-A/B")'
    tokenizer.add_special_case("_SPECIAL_", [{"orth": "_SPECIAL_"}])
    tokenizer.add_special_case("A/B", [{"orth": "A/B"}])
    doc = tokenizer(text)
    assert [token.text for token in doc] == [
        "(",
        "(",
        "(",
        "_SPECIAL_",
        "A/B",
        ",",
        "A/B",
        "-",
        "A/B",
        '"',
        ")",
    ]


def test_tokenizer_special_cases_with_affixes_preserve_spacy():
    tokenizer = English().tokenizer
    # reset all special cases
    tokenizer.rules = {}

    # in-place modification (only merges)
    text = "''a'' "
    tokenizer.add_special_case("''", [{"ORTH": "''"}])
    assert tokenizer(text).text == text

    # not in-place (splits and merges)
    tokenizer.add_special_case("ab", [{"ORTH": "a"}, {"ORTH": "b"}])
    text = "ab ab ab ''ab ab'' ab'' ''ab"
    assert tokenizer(text).text == text


def test_tokenizer_special_cases_with_period(tokenizer):
    text = "_SPECIAL_."
    tokenizer.add_special_case("_SPECIAL_", [{"orth": "_SPECIAL_"}])
    doc = tokenizer(text)
    assert [token.text for token in doc] == ["_SPECIAL_", "."]


def test_tokenizer_special_cases_idx(tokenizer):
    text = "the _ID'X_"
    tokenizer.add_special_case("_ID'X_", [{"orth": "_ID"}, {"orth": "'X_"}])
    doc = tokenizer(text)
    assert doc[1].idx == 4
    assert doc[2].idx == 7


def test_tokenizer_special_cases_spaces(tokenizer):
    assert [t.text for t in tokenizer("a b c")] == ["a", "b", "c"]
    tokenizer.add_special_case("a b c", [{"ORTH": "a b c"}])
    assert [t.text for t in tokenizer("a b c")] == ["a b c"]


def test_tokenizer_flush_cache(en_vocab):
    suffix_re = re.compile(r"[\.]$")
    tokenizer = Tokenizer(
        en_vocab,
        suffix_search=suffix_re.search,
    )
    assert [t.text for t in tokenizer("a.")] == ["a", "."]
    tokenizer.suffix_search = None
    assert [t.text for t in tokenizer("a.")] == ["a."]


def test_tokenizer_flush_specials(en_vocab):
    suffix_re = re.compile(r"[\.]$")
    rules = {"a a": [{"ORTH": "a a"}]}
    tokenizer1 = Tokenizer(
        en_vocab,
        suffix_search=suffix_re.search,
        rules=rules,
    )
    assert [t.text for t in tokenizer1("a a.")] == ["a a", "."]
    tokenizer1.rules = {}
    assert [t.text for t in tokenizer1("a a.")] == ["a", "a", "."]


def test_tokenizer_prefix_suffix_overlap_lookbehind(en_vocab):
    # the prefix and suffix matches overlap in the suffix lookbehind
    prefixes = ["a(?=.)"]
    suffixes = [r"(?<=\w)\.", r"(?<=a)\d+\."]
    prefix_re = compile_prefix_regex(prefixes)
    suffix_re = compile_suffix_regex(suffixes)
    tokenizer = Tokenizer(
        en_vocab,
        prefix_search=prefix_re.search,
        suffix_search=suffix_re.search,
    )
    tokens = [t.text for t in tokenizer("a10.")]
    assert tokens == ["a", "10", "."]
    explain_tokens = [t[1] for t in tokenizer.explain("a10.")]
    assert tokens == explain_tokens


def test_tokenizer_infix_prefix(en_vocab):
    # the prefix and suffix matches overlap in the suffix lookbehind
    infixes = ["±"]
    suffixes = ["%"]
    infix_re = compile_infix_regex(infixes)
    suffix_re = compile_suffix_regex(suffixes)
    tokenizer = Tokenizer(
        en_vocab,
        infix_finditer=infix_re.finditer,
        suffix_search=suffix_re.search,
    )
    tokens = [t.text for t in tokenizer("±10%")]
    assert tokens == ["±10", "%"]
    explain_tokens = [t[1] for t in tokenizer.explain("±10%")]
    assert tokens == explain_tokens


@pytest.mark.issue(10086)
def test_issue10086(en_tokenizer):
    """Test special case works when part of infix substring."""
    text = "No--don't see"

    # without heuristics: do n't
    en_tokenizer.faster_heuristics = False
    doc = en_tokenizer(text)
    assert "n't" in [w.text for w in doc]
    assert "do" in [w.text for w in doc]

    # with (default) heuristics: don't
    en_tokenizer.faster_heuristics = True
    doc = en_tokenizer(text)
    assert "don't" in [w.text for w in doc]


def test_tokenizer_initial_special_case_explain(en_vocab):
    tokenizer = Tokenizer(
        en_vocab,
        token_match=re.compile("^id$").match,
        rules={
            "id": [{"ORTH": "i"}, {"ORTH": "d"}],
        },
    )
    tokens = [t.text for t in tokenizer("id")]
    explain_tokens = [t[1] for t in tokenizer.explain("id")]
    assert tokens == explain_tokens
