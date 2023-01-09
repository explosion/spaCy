import pytest
from spacy.lang.sv.lex_attrs import like_num


@pytest.mark.parametrize(
    "text,match",
    [
        ("10", True),
        ("1", True),
        ("10.000", True),
        ("10.00", True),
        ("999,0", True),
        ("en", True),
        ("två", True),
        ("miljard", True),
        ("hund", False),
        (",", False),
        ("1/2", True),
    ],
)
def test_lex_attrs_like_number(sv_tokenizer, text, match):
    tokens = sv_tokenizer(text)
    assert len(tokens) == 1
    assert tokens[0].like_num == match


@pytest.mark.parametrize("word", ["elva"])
def test_sv_lex_attrs_capitals(word):
    assert like_num(word)
    assert like_num(word.upper())
