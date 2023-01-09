import pytest


@pytest.mark.parametrize(
    "text,match",
    [
        ("ι", True),
        ("α", True),
        ("ϟα", True),
        ("ἑκατόν", True),
        ("ἐνακόσια", True),
        ("δισχίλια", True),
        ("μύρια", True),
        ("εἷς", True),
        ("λόγος", False),
        (",", False),
        ("λβ", True),
    ],
)
def test_lex_attrs_like_number(grc_tokenizer, text, match):
    tokens = grc_tokenizer(text)
    assert len(tokens) == 1
    assert tokens[0].like_num == match
