import pytest

from spacy.hu import Hungarian


@pytest.fixture(scope="session")
def HU():
    return Hungarian()


@pytest.fixture(scope="module")
def hu_tokenizer(HU):
    return HU.tokenizer


@pytest.mark.parametrize(("input_str", "expected_length"), [
    ("A vs. egy", 3),
    ("A dr. egy", 3),
    ("A .hu egy tld.", 5),
    ("A .hu.", 3),
    ("Az egy.ketto pelda.", 4),
    ("A pl. rovidites.", 4),
    ("A S.M.A.R.T. szo.", 4)
])
def test_abbreviations(hu_tokenizer, input_str, expected_length):
    tokens = hu_tokenizer(input_str)
    assert len(tokens) == expected_length
