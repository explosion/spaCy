import pytest


@pytest.mark.parametrize(
    "text,like_num,norm,prefix,suffix",
    [
        ("нула", True, "nula", "n", "ula"),
        ("Казна", False, "kazna", "K", "zna"),
    ],
)
def test_lex_attrs(sr_tokenizer, text, like_num, norm, prefix, suffix):
    tokens = sr_tokenizer(text)
    assert len(tokens) == 1
    assert tokens[0].like_num == like_num
    assert tokens[0].norm_ == norm
    assert tokens[0].prefix_ == prefix
    assert tokens[0].suffix_ == suffix
