import pytest


def test_sa_tokenizer_handles_long_text(sa_tokenizer):
    text = """नानाविधानि दिव्यानि नानावर्णाकृतीनि च।।"""
    tokens = sa_tokenizer(text)
    assert len(tokens) == 6


@pytest.mark.parametrize(
    "text,length",
    [
        ("श्री भगवानुवाच पश्य मे पार्थ रूपाणि शतशोऽथ सहस्रशः।", 9),
        ("गुणान् सर्वान् स्वभावो मूर्ध्नि वर्तते ।", 6),
    ],
)
def test_sa_tokenizer_handles_cnts(sa_tokenizer, text, length):
    tokens = sa_tokenizer(text)
    assert len(tokens) == length


@pytest.mark.parametrize(
    "text,match",
    [
        ("10", True),
        ("1", True),
        ("10.000", True),
        ("1000", True),
        ("999,0", True),
        ("एकः ", True),
        ("दश", True),
        ("पञ्चदश", True),
        ("चत्वारिंशत् ", True),
        ("कूपे", False),
        (",", False),
        ("1/2", True),
    ],
)
def test_lex_attrs_like_number(sa_tokenizer, text, match):
    tokens = sa_tokenizer(text)
    assert len(tokens) == 1
    assert tokens[0].like_num == match
