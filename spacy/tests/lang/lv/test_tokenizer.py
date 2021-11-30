import pytest

LV_BASIC_TOKENIZATION_TESTS = [
    (
        "Nevienu nedrīkst spīdzināt vai cietsirdīgi vai pazemojoši ar viņu "
        "apieties vai sodīt.",
        [
            "Nevienu",
            "nedrīkst",
            "spīdzināt",
            "vai",
            "cietsirdīgi",
            "vai",
            "pazemojoši",
            "ar",
            "viņu",
            "apieties",
            "vai",
            "sodīt",
            ".",
        ],
    ),
]


@pytest.mark.parametrize("text,expected_tokens", LV_BASIC_TOKENIZATION_TESTS)
def test_lv_tokenizer_basic(lv_tokenizer, text, expected_tokens):
    tokens = lv_tokenizer(text)
    token_list = [token.text for token in tokens if not token.is_space]
    assert expected_tokens == token_list
