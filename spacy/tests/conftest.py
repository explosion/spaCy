from spacy.en import English

import pytest
import os


@pytest.fixture(scope="session")
def EN():
    if os.environ.get('SPACY_DATA'):
        data_dir = os.environ.get('SPACY_DATA')
    else:
        data_dir = None
    print("Load EN from %s" % data_dir)
    return English(data_dir=data_dir)


def pytest_addoption(parser):
    parser.addoption("--models", action="store_true",
        help="include tests that require full models")
    parser.addoption("--vectors", action="store_true",
        help="include word vectors tests")
    parser.addoption("--slow", action="store_true",
        help="include slow tests")



def pytest_runtest_setup(item):
    for opt in ['models', 'vectors', 'slow']:
        if opt in item.keywords and not item.config.getoption("--%s" % opt):
            pytest.skip("need --%s option to run" % opt)
