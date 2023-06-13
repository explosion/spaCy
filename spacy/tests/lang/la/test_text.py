import pytest

from spacy.lang.la.lex_attrs import like_num


@pytest.mark.parametrize(
    "text,match",
    [
        ("IIII", True),
        ("VI", True),
        ("vi", True),
        ("IV", True),
        ("iv", True),
        ("IX", True),
        ("ix", True),
        ("MMXXII", True),
        ("0", True),
        ("1", True),
        ("quattuor", True),
        ("decem", True),
        ("tertius", True),
        ("canis", False),
        ("MMXX11", False),
        (",", False),
    ],
)
def test_lex_attrs_like_number(la_tokenizer, text, match):
    tokens = la_tokenizer(text)
    assert len(tokens) == 1
    assert tokens[0].like_num == match


@pytest.mark.parametrize("word", ["quinque"])
def test_la_lex_attrs_capitals(word):
    assert like_num(word)
    assert like_num(word.upper())
