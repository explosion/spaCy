import pytest


# fmt: off
GA_TOKEN_EXCEPTION_TESTS = [
    ("Niall Ó Domhnaill, Rialtas na hÉireann 1977 (lch. 600).", ["Niall", "Ó", "Domhnaill", ",", "Rialtas", "na", "hÉireann", "1977", "(", "lch.", "600", ")", "."]),
    ("Daoine a bhfuil Gaeilge acu, m.sh. tusa agus mise", ["Daoine", "a", "bhfuil", "Gaeilge", "acu", ",", "m.sh.", "tusa", "agus", "mise"])
]
# fmt: on


@pytest.mark.parametrize("text,expected_tokens", GA_TOKEN_EXCEPTION_TESTS)
def test_ga_tokenizer_handles_exception_cases(ga_tokenizer, text, expected_tokens):
    tokens = ga_tokenizer(text)
    token_list = [token.text for token in tokens if not token.is_space]
    assert expected_tokens == token_list
