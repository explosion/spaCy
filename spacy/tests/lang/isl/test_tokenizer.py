import pytest

IS_BASIC_TOKENIZATION_TESTS = [
    (
        "Enginn maður skal sæta pyndingum eða ómannlegri eða "
        "vanvirðandi meðferð eða refsingu. ",
        [
            "Enginn",
            "maður",
            "skal",
            "sæta",
            "pyndingum",
            "eða",
            "ómannlegri",
            "eða",
            "vanvirðandi",
            "meðferð",
            "eða",
            "refsingu",
            ".",
        ],
    ),
]


@pytest.mark.parametrize("text,expected_tokens", IS_BASIC_TOKENIZATION_TESTS)
def test_is_tokenizer_basic(is_tokenizer, text, expected_tokens):
    tokens = is_tokenizer(text)
    token_list = [token.text for token in tokens if not token.is_space]
    assert expected_tokens == token_list
