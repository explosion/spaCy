import pytest

XX_BASIC_TOKENIZATION_TESTS = [
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


@pytest.mark.parametrize("text,expected_tokens", XX_BASIC_TOKENIZATION_TESTS)
def test_xx_tokenizer_basic(xx_tokenizer, text, expected_tokens):
    tokens = xx_tokenizer(text)
    token_list = [token.text for token in tokens if not token.is_space]
    assert expected_tokens == token_list
