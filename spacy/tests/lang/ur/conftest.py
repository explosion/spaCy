import pytest

from spacy.util import get_lang_class


@pytest.fixture(scope="session")
def ur_tokenizer():
    return get_lang_class("ur")().tokenizer
