import pytest


@pytest.mark.parametrize(
    "text,match",
    [
        ("10", True),
        ("1", True),
        ("10,000", True),
        ("10,00", True),
        ("jedne", True),
        ("dwanaće", True),
        ("milion", True),
        ("sto", True),
        ("załožene", False),
        ("wona", False),
        ("powšitkownej", False),
        (",", False),
        ("1/2", True),
    ],
)
def test_lex_attrs_like_number(hsb_tokenizer, text, match):
    tokens = hsb_tokenizer(text)
    assert len(tokens) == 1
    assert tokens[0].like_num == match
