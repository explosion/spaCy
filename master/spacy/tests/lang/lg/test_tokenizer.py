import pytest

LG_BASIC_TOKENIZATION_TESTS = [
    (
        "Abooluganda ab’emmamba ababiri",
        ["Abooluganda", "ab’emmamba", "ababiri"],
    ),
]


@pytest.mark.parametrize("text,expected_tokens", LG_BASIC_TOKENIZATION_TESTS)
def test_lg_tokenizer_basic(lg_tokenizer, text, expected_tokens):
    tokens = lg_tokenizer(text)
    token_list = [token.text for token in tokens if not token.is_space]
    assert expected_tokens == token_list
