import pytest
from spacy.en import English


@pytest.fixture(scope="session")
def EN():
    return English()
