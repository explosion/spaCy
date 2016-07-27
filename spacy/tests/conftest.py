import pytest
import os

import spacy

@pytest.fixture(scope="session")
def EN():
    return spacy.load("en")

@pytest.fixture(scope="session")
def DE():
    return spacy.load("de")


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
