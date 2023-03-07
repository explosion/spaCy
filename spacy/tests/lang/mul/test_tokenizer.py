import pytest

MUL_BASIC_TOKENIZATION_TESTS = [
    (
        "Lääʹddjânnmest lie nuʹtt 10 000 säʹmmliʹžžed. Seeʹst pâʹjjel",
        [
            "Lääʹddjânnmest",
            "lie",
            "nuʹtt",
            "10",
            "000",
            "säʹmmliʹžžed",
            ".",
            "Seeʹst",
            "pâʹjjel",
        ],
    ),
]


@pytest.mark.parametrize("text,expected_tokens", MUL_BASIC_TOKENIZATION_TESTS)
def test_mul_tokenizer_basic(mul_tokenizer, text, expected_tokens):
    tokens = mul_tokenizer(text)
    token_list = [token.text for token in tokens if not token.is_space]
    assert expected_tokens == token_list
