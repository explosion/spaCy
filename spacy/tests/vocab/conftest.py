import pytest


@pytest.fixture(scope="session")
def en_vocab(EN):
    return EN.vocab
