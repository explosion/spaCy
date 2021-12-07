import pytest

SQ_BASIC_TOKENIZATION_TESTS = [
    (
        "Askush nuk mund t’i nënshtrohet torturës ose dënimeve ose "
        "trajtimeve çnjerëzore ose poshtëruese.",
        [
            "Askush",
            "nuk",
            "mund",
            "t’i",
            "nënshtrohet",
            "torturës",
            "ose",
            "dënimeve",
            "ose",
            "trajtimeve",
            "çnjerëzore",
            "ose",
            "poshtëruese",
            ".",
        ],
    ),
]


@pytest.mark.parametrize("text,expected_tokens", SQ_BASIC_TOKENIZATION_TESTS)
def test_sq_tokenizer_basic(sq_tokenizer, text, expected_tokens):
    tokens = sq_tokenizer(text)
    token_list = [token.text for token in tokens if not token.is_space]
    assert expected_tokens == token_list
