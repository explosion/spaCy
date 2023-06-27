import pytest

from spacy.attrs import ENT_IOB, IS_ALPHA, LEMMA, NORM, ORTH, intify_attrs
from spacy.lang.en.stop_words import STOP_WORDS
from spacy.lang.lex_attrs import (
    is_ascii,
    is_currency,
    is_punct,
    is_stop,
    like_url,
    word_shape,
)


@pytest.mark.parametrize("word", ["the"])
@pytest.mark.issue(1889)
def test_issue1889(word):
    assert is_stop(word, STOP_WORDS) == is_stop(word.upper(), STOP_WORDS)


@pytest.mark.parametrize("text", ["dog"])
def test_attrs_key(text):
    assert intify_attrs({"ORTH": text}) == {ORTH: text}
    assert intify_attrs({"NORM": text}) == {NORM: text}
    assert intify_attrs({"lemma": text}, strings_map={text: 10}) == {LEMMA: 10}


@pytest.mark.parametrize("text", ["dog"])
def test_attrs_idempotence(text):
    int_attrs = intify_attrs({"lemma": text, "is_alpha": True}, strings_map={text: 10})
    assert intify_attrs(int_attrs) == {LEMMA: 10, IS_ALPHA: True}


@pytest.mark.parametrize("text", ["dog"])
def test_attrs_do_deprecated(text):
    int_attrs = intify_attrs(
        {"F": text, "is_alpha": True}, strings_map={text: 10}, _do_deprecated=True
    )
    assert int_attrs == {ORTH: 10, IS_ALPHA: True}


def test_attrs_ent_iob_intify():
    int_attrs = intify_attrs({"ENT_IOB": ""})
    assert int_attrs == {ENT_IOB: 0}

    int_attrs = intify_attrs({"ENT_IOB": "I"})
    assert int_attrs == {ENT_IOB: 1}

    int_attrs = intify_attrs({"ENT_IOB": "O"})
    assert int_attrs == {ENT_IOB: 2}

    int_attrs = intify_attrs({"ENT_IOB": "B"})
    assert int_attrs == {ENT_IOB: 3}

    int_attrs = intify_attrs({ENT_IOB: ""})
    assert int_attrs == {ENT_IOB: 0}

    int_attrs = intify_attrs({ENT_IOB: "I"})
    assert int_attrs == {ENT_IOB: 1}

    int_attrs = intify_attrs({ENT_IOB: "O"})
    assert int_attrs == {ENT_IOB: 2}

    int_attrs = intify_attrs({ENT_IOB: "B"})
    assert int_attrs == {ENT_IOB: 3}

    with pytest.raises(ValueError):
        int_attrs = intify_attrs({"ENT_IOB": "XX"})

    with pytest.raises(ValueError):
        int_attrs = intify_attrs({ENT_IOB: "XX"})


@pytest.mark.parametrize("text,match", [(",", True), (" ", False), ("a", False)])
def test_lex_attrs_is_punct(text, match):
    assert is_punct(text) == match


@pytest.mark.parametrize("text,match", [(",", True), ("£", False), ("♥", False)])
def test_lex_attrs_is_ascii(text, match):
    assert is_ascii(text) == match


@pytest.mark.parametrize(
    "text,match",
    [
        ("$", True),
        ("£", True),
        ("♥", False),
        ("€", True),
        ("¥", True),
        ("¢", True),
        ("a", False),
        ("www.google.com", False),
        ("dog", False),
    ],
)
def test_lex_attrs_is_currency(text, match):
    assert is_currency(text) == match


@pytest.mark.parametrize(
    "text,match",
    [
        ("www.google.com", True),
        ("google.com", True),
        ("sydney.com", True),
        ("1abc2def.org", True),
        ("http://stupid", True),
        ("www.hi", True),
        ("example.com/example", True),
        ("dog", False),
        ("1.2", False),
        ("1.a", False),
        ("hello.There", False),
    ],
)
def test_lex_attrs_like_url(text, match):
    assert like_url(text) == match


@pytest.mark.parametrize(
    "text,shape",
    [
        ("Nasa", "Xxxx"),
        ("capitalized", "xxxx"),
        ("999999999", "dddd"),
        ("C3P0", "XdXd"),
        (",", ","),
        ("\n", "\n"),
        ("``,-", "``,-"),
    ],
)
def test_lex_attrs_word_shape(text, shape):
    assert word_shape(text) == shape
