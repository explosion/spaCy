import pytest

# Expected tokenizations follow the Czech Universal Dependencies treebanks
# (e.g. UD_Czech-PDT), where the period of an abbreviation or an initial is a
# separate token.
CS_TOKENIZER_TESTS = [
    ("J. Novák", ["J", ".", "Novák"]),
    ("např. v r. 1992", ["např", ".", "v", "r", ".", "1992"]),
    ("Beta, a.s., Olomouc", ["Beta", ",", "a", ".", "s", ".", ",", "Olomouc"]),
    ("ABC s.r.o.", ["ABC", "s", ".", "r", ".", "o", "."]),
    ("Ing. Jan Novák, Ph.D.", ["Ing", ".", "Jan", "Novák", ",", "Ph", ".", "D", "."]),
    ("v I. pořadí", ["v", "I", ".", "pořadí"]),
    ("Dne 13. 7. 1994", ["Dne", "13", ".", "7", ".", "1994"]),
]


@pytest.mark.parametrize("text,expected_tokens", CS_TOKENIZER_TESTS)
def test_cs_tokenizer_handles_testcases(cs_tokenizer, text, expected_tokens):
    tokens = cs_tokenizer(text)
    assert [token.text for token in tokens if not token.is_space] == expected_tokens


@pytest.mark.parametrize(
    "text", ["137.10", "10.000", "1/2", "jan.novak@seznam.cz", "www.seznam.cz"]
)
def test_cs_tokenizer_keeps_numbers_emails_and_urls(cs_tokenizer, text):
    tokens = cs_tokenizer(text)
    assert len(tokens) == 1
