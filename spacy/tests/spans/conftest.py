import pytest
from spacy.en import English
import os


@pytest.fixture(scope="session")
def en_nlp():
    return English()
