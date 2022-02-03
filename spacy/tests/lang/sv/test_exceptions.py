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


@pytest.mark.issue(805)
@pytest.mark.parametrize(
    "text,expected_tokens",
    [
        (
            "Smörsåsen används bl.a. till fisk",
            ["Smörsåsen", "används", "bl.a.", "till", "fisk"],
        ),
        (
            "Jag kommer först kl. 13 p.g.a. diverse förseningar",
            ["Jag", "kommer", "först", "kl.", "13", "p.g.a.", "diverse", "förseningar"],
        ),
    ],
)
def test_issue805(sv_tokenizer, text, expected_tokens):
    tokens = sv_tokenizer(text)
    token_list = [token.text for token in tokens if not token.is_space]
    assert expected_tokens == token_list


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


@pytest.mark.parametrize("text", ["bl.a", "m.a.o.", "Jan.", "Dec.", "kr.", "osv."])
def test_sv_tokenizer_handles_abbr(sv_tokenizer, text):
    tokens = sv_tokenizer(text)
    assert len(tokens) == 1


@pytest.mark.parametrize("text", ["Jul.", "jul.", "sön.", "Sön."])
def test_sv_tokenizer_handles_ambiguous_abbr(sv_tokenizer, text):
    tokens = sv_tokenizer(text)
    assert len(tokens) == 2


def test_sv_tokenizer_handles_exc_in_text(sv_tokenizer):
    text = "Det är bl.a. inte meningen"
    tokens = sv_tokenizer(text)
    assert len(tokens) == 5
    assert tokens[2].text == "bl.a."


def test_sv_tokenizer_handles_custom_base_exc(sv_tokenizer):
    text = "Här är något du kan titta på."
    tokens = sv_tokenizer(text)
    assert len(tokens) == 8
    assert tokens[6].text == "på"
    assert tokens[7].text == "."
