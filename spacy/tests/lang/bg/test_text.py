import pytest


@pytest.mark.parametrize(
    "word,match",
    [
        ("10", True),
        ("1", True),
        ("10000", True),
        ("1.000", True),
        ("бројка", False),
        ("999,23", True),
        ("едно", True),
        ("две", True),
        ("цифра", False),
        ("единайсет", True),
        ("десет", True),
        ("сто", True),
        ("брой", False),
        ("хиляда", True),
        ("милион", True),
        (",", False),
        ("милиарда", True),
        ("билион", True),
    ],
)
def test_bg_lex_attrs_like_number(bg_tokenizer, word, match):
    tokens = bg_tokenizer(word)
    assert len(tokens) == 1
    assert tokens[0].like_num == match
