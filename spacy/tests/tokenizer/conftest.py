import pytest
from ...en import English


@pytest.fixture
def en_tokenizer():
    return English.Defaults.create_tokenizer()
