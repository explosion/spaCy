import pytest
from spacy.en import English


@pytest.fixture(scope="module")
def en_tokenizer(EN):
    return EN.tokenizer
