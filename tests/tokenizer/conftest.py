import pytest
from spacy.en import English


@pytest.fixture(scope="session")
def EN():
    return English(load_vectors=False)

@pytest.fixture(scope="session")
def en_tokenizer(EN):
    return EN.tokenizer
