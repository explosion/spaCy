import pytest

HR_BASIC_TOKENIZATION_TESTS = [
    (
        "Nitko se ne smije podvrgnuti mučenju ni nečovječnom ili "
        "ponižavajućem postupanju ili kazni.",
        [
            "Nitko",
            "se",
            "ne",
            "smije",
            "podvrgnuti",
            "mučenju",
            "ni",
            "nečovječnom",
            "ili",
            "ponižavajućem",
            "postupanju",
            "ili",
            "kazni",
            ".",
        ],
    ),
]


@pytest.mark.parametrize("text,expected_tokens", HR_BASIC_TOKENIZATION_TESTS)
def test_hr_tokenizer_basic(hr_tokenizer, text, expected_tokens):
    tokens = hr_tokenizer(text)
    token_list = [token.text for token in tokens if not token.is_space]
    assert expected_tokens == token_list
