import pytest

HSB_BASIC_TOKENIZATION_TESTS = [
    (
        "Hornjoserbšćina wobsteji resp. wobsteješe z wjacorych dialektow, kotrež so zdźěla chětro wot so rozeznawachu.",
        [
            "Hornjoserbšćina",
            "wobsteji",
            "resp.",
            "wobsteješe",
            "z",
            "wjacorych",
            "dialektow",
            ",",
            "kotrež",
            "so",
            "zdźěla",
            "chětro",
            "wot",
            "so",
            "rozeznawachu",
            ".",
        ],
    ),
]


@pytest.mark.parametrize("text,expected_tokens", HSB_BASIC_TOKENIZATION_TESTS)
def test_hsb_tokenizer_basic(hsb_tokenizer, text, expected_tokens):
    tokens = hsb_tokenizer(text)
    token_list = [token.text for token in tokens if not token.is_space]
    assert expected_tokens == token_list
