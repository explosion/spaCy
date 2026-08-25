import pytest

from spacy.lang.pt.lex_attrs import like_num


@pytest.mark.parametrize(
    "text,match",
    [
        ("10", True),
        ("1", True),
        ("10,000", True),
        ("10,00", True),
        ("999.0", True),
        ("um", True),
        ("dois", True),
        ("bilhão", True),
        ("vinte", True),
        ("cachorro", False),
        (",", False),
        ("1/2", True),
        ("duas", True),
    ],
)
def test_pt_lex_attrs_like_number(pt_tokenizer, text, match):
    tokens = pt_tokenizer(text)
    assert len(tokens) == 1
    assert tokens[0].like_num == match


@pytest.mark.parametrize(
    "word", ["terceiro", "décimos", "Milionésimo", "100.º", "Centésimo", "9.ª"]
)
def test_pt_lex_attrs_like_number_for_ordinal(word):
    assert like_num(word)


@pytest.mark.parametrize("word", ["onze", "quadragésimo"])
def test_pt_lex_attrs_capitals(word):
    assert like_num(word)
    assert like_num(word.upper())
