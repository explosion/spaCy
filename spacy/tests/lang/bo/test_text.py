import pytest


@pytest.mark.parametrize(
    "text,match",
    [
        ("10", True),
        ("1", True),
        ("999.0", True),
        ("གཅིག་", True),
        ("གཉིས་", True),
        ("ཀླད་ཀོར་", True),
        ("བཅུ་གཅིག་", True),
        ("ཁྱི་", False),
        (",", False),
    ],
)
def test_lex_attrs_like_number(bo_tokenizer, text, match):
    tokens = bo_tokenizer(text)
    assert len(tokens) == 1
    assert tokens[0].like_num == match
