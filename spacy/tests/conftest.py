# coding: utf-8
from __future__ import unicode_literals

from ..en import English
from ..de import German
from ..es import Spanish
from ..it import Italian
from ..fr import French
from ..pt import Portuguese
from ..nl import Dutch
from ..sv import Swedish
from ..hu import Hungarian
from ..fi import Finnish
from ..tokens import Doc
from ..strings import StringStore
from ..lemmatizer import Lemmatizer
from ..attrs import ORTH, TAG, HEAD, DEP
from ..util import match_best_version, get_data_path

from io import StringIO, BytesIO
from pathlib import Path
import os
import pytest


LANGUAGES = [English, German, Spanish, Italian, French, Portuguese, Dutch,
             Swedish, Hungarian, Finnish]


@pytest.fixture(params=LANGUAGES)
def tokenizer(request):
    lang = request.param
    return lang.Defaults.create_tokenizer()


@pytest.fixture
def en_tokenizer():
    return English.Defaults.create_tokenizer()


@pytest.fixture
def en_vocab():
    return English.Defaults.create_vocab()


@pytest.fixture
def en_parser():
    return English.Defaults.create_parser()


@pytest.fixture
def de_tokenizer():
    return German.Defaults.create_tokenizer()


@pytest.fixture(scope='module')
def fr_tokenizer():
    return French.Defaults.create_tokenizer()


@pytest.fixture
def hu_tokenizer():
    return Hungarian.Defaults.create_tokenizer()


@pytest.fixture
def fi_tokenizer():
    return Finnish.Defaults.create_tokenizer()


@pytest.fixture
def sv_tokenizer():
    return Swedish.Defaults.create_tokenizer()


@pytest.fixture
def stringstore():
    return StringStore()


@pytest.fixture
def en_entityrecognizer():
     return English.Defaults.create_entity()


@pytest.fixture
def lemmatizer(path):
    if path is not None:
        return Lemmatizer.load(path)
    else:
        return None


@pytest.fixture
def text_file():
    return StringIO()

@pytest.fixture
def text_file_b():
    return BytesIO()


@pytest.fixture
def path():
    if 'SPACY_DATA' in os.environ:
        return Path(os.environ['SPACY_DATA'])
    else:
        return match_best_version('en', None, get_data_path())


# only used for tests that require loading the models
# in all other cases, use specific instances
@pytest.fixture(scope="session")
def EN():
    return English()


@pytest.fixture(scope="session")
def DE():
    return German()


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
