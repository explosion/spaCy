import pytest


@pytest.mark.parametrize(
    "text,match",
    [
        ("10", True),
        ("1", True),
        ("10,000", True),
        ("10,00", True),
        ("jadno", True),
        ("dwanassćo", True),
        ("milion", True),
        ("sto", True),
        ("ceła", False),
        ("kopica", False),
        ("narěcow", False),
        (",", False),
        ("1/2", True),
    ],
)
def test_lex_attrs_like_number(dsb_tokenizer, text, match):
    tokens = dsb_tokenizer(text)
    assert len(tokens) == 1
    assert tokens[0].like_num == match
