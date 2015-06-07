import pytest
from spacy.en import English


@pytest.fixture(scope="session")
def en_nlp():
    return English(load_vectors=False)
