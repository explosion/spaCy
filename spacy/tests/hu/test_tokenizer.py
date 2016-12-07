import pytest

from spacy.hu import Hungarian


@pytest.fixture(scope="session")
def HU():
    return Hungarian()


@pytest.fixture(scope="module")
def hu_tokenizer(HU):
    return HU.tokenizer


def test_abbreviations(hu_tokenizer):
    tokens = hu_tokenizer("A vs. egy")
    assert len(tokens) == 3

    tokens = hu_tokenizer("A dr. egy")
    assert len(tokens) == 3
