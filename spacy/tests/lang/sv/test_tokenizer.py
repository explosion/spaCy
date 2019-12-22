import pytest


SV_TOKEN_EXCEPTION_TESTS = [
    (
        "Smörsåsen används bl.a. till fisk",
        ["Smörsåsen", "används", "bl.a.", "till", "fisk"],
    ),
    (
        "Jag kommer först kl. 13 p.g.a. diverse förseningar",
        ["Jag", "kommer", "först", "kl.", "13", "p.g.a.", "diverse", "förseningar"],
    ),
    (
        "Anders I. tycker om ord med i i.",
        ["Anders", "I.", "tycker", "om", "ord", "med", "i", "i", "."],
    ),
]


@pytest.mark.parametrize("text,expected_tokens", SV_TOKEN_EXCEPTION_TESTS)
def test_sv_tokenizer_handles_exception_cases(sv_tokenizer, text, expected_tokens):
    tokens = sv_tokenizer(text)
    token_list = [token.text for token in tokens if not token.is_space]
    assert expected_tokens == token_list


@pytest.mark.parametrize("text", ["driveru", "hajaru", "Serru", "Fixaru"])
def test_sv_tokenizer_handles_verb_exceptions(sv_tokenizer, text):
    tokens = sv_tokenizer(text)
    assert len(tokens) == 2
    assert tokens[1].text == "u"
