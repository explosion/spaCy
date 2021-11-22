import pytest

SL_BASIC_TOKENIZATION_TESTS = [
    (
        "Vsakdo ima pravico do spoštovanja njegovega zasebnega in "
        "družinskega življenja, doma in dopisovanja.",
        [
            "Vsakdo",
            "ima",
            "pravico",
            "do",
            "spoštovanja",
            "njegovega",
            "zasebnega",
            "in",
            "družinskega",
            "življenja",
            ",",
            "doma",
            "in",
            "dopisovanja",
            ".",
        ],
    ),
]


@pytest.mark.parametrize("text,expected_tokens", SL_BASIC_TOKENIZATION_TESTS)
def test_sl_tokenizer_basic(sl_tokenizer, text, expected_tokens):
    tokens = sl_tokenizer(text)
    token_list = [token.text for token in tokens if not token.is_space]
    assert expected_tokens == token_list
