import pytest

DSB_BASIC_TOKENIZATION_TESTS = [
    (
        "Ale eksistěrujo mimo togo ceła kopica narěcow, ako na pśikład slěpjańska.",
        [
            "Ale",
            "eksistěrujo",
            "mimo",
            "togo",
            "ceła",
            "kopica",
            "narěcow",
            ",",
            "ako",
            "na",
            "pśikład",
            "slěpjańska",
            ".",
        ],
    ),
]


@pytest.mark.parametrize("text,expected_tokens", DSB_BASIC_TOKENIZATION_TESTS)
def test_dsb_tokenizer_basic(dsb_tokenizer, text, expected_tokens):
    tokens = dsb_tokenizer(text)
    token_list = [token.text for token in tokens if not token.is_space]
    assert expected_tokens == token_list
