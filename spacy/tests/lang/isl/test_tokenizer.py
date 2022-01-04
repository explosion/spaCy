import pytest

IC_BASIC_TOKENIZATION_TESTS = [
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


@pytest.mark.parametrize("text,expected_tokens", IC_BASIC_TOKENIZATION_TESTS)
def test_ic_tokenizer_basic(ic_tokenizer, text, expected_tokens):
    tokens = ic_tokenizer(text)
    token_list = [token.text for token in tokens if not token.is_space]
    assert expected_tokens == token_list
