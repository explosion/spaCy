import pytest

NB_TOKEN_EXCEPTION_TESTS = [
    (
        "Smørsausen brukes bl.a. til fisk",
        ["Smørsausen", "brukes", "bl.a.", "til", "fisk"],
    ),
    (
        "Jeg kommer først kl. 13 pga. diverse forsinkelser",
        ["Jeg", "kommer", "først", "kl.", "13", "pga.", "diverse", "forsinkelser"],
    ),
]


@pytest.mark.parametrize("text,expected_tokens", NB_TOKEN_EXCEPTION_TESTS)
def test_nb_tokenizer_handles_exception_cases(nb_tokenizer, text, expected_tokens):
    tokens = nb_tokenizer(text)
    token_list = [token.text for token in tokens if not token.is_space]
    assert expected_tokens == token_list
