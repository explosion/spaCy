import pytest

SK_BASIC_TOKENIZATION_TESTS = [
    (
        "Kedy sa narodil Andrej Kiska?",
        ["Kedy", "sa", "narodil", "Andrej", "Kiska", "?"],
    ),
]


@pytest.mark.parametrize("text,expected_tokens", SK_BASIC_TOKENIZATION_TESTS)
def test_sk_tokenizer_basic(sk_tokenizer, text, expected_tokens):
    tokens = sk_tokenizer(text)
    token_list = [token.text for token in tokens if not token.is_space]
    assert expected_tokens == token_list
