import pytest

from spacy.lang.kmr.lex_attrs import like_num


@pytest.mark.parametrize(
    "word",
    [
        "yekem",
        "duyemîn",
        "100em",
        "dehem",
        "sedemîn",
        "34em",
        "30yem",
        "20emîn",
        "50yemîn",
    ],
)
def test_kmr_lex_attrs_like_number_for_ordinal(word):
    assert like_num(word)


@pytest.mark.parametrize("word", ["deh"])
def test_kmr_lex_attrs_capitals(word):
    assert like_num(word)
    assert like_num(word.upper())
