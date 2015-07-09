import pytest
from spacy.en import English, LOCAL_DATA_DIR
import os


@pytest.fixture(scope="session")
def EN():
    data_dir = os.environ.get('SPACY_DATA', LOCAL_DATA_DIR)
    return English(data_dir=data_dir)
