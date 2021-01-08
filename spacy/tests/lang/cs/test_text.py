import pytest


@pytest.mark.parametrize(
    "text,match",
    [
        ("10", True),
        ("1", True),
        ("10.000", True),
        ("1000", True),
        ("999,0", True),
        ("devatenáct", True),
        ("osmdesát", True),
        ("kvadrilion", True),
        ("Pes", False),
        (",", False),
        ("1/2", True),
    ],
)
def test_lex_attrs_like_number(cs_tokenizer, text, match):
    tokens = cs_tokenizer(text)
    assert len(tokens) == 1
    assert tokens[0].like_num == match
