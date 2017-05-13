# coding: utf-8
from __future__ import unicode_literals

from ..tokens import Doc
from ..strings import StringStore
from ..lemmatizer import Lemmatizer
from ..attrs import ORTH, TAG, HEAD, DEP
from .. import util

from io import StringIO, BytesIO
from pathlib import Path
import pytest


_languages = ['bn', 'da', 'de', 'en', 'es', 'fi', 'fr', 'he', 'hu', 'it', 'nb',
              'nl', 'pl', 'pt', 'sv']


@pytest.fixture(params=_languages)
def tokenizer(request):
    lang = util.load_lang_class(request.param)
    return lang.Defaults.create_tokenizer()


@pytest.fixture
def en_tokenizer():
    return util.load_lang_class('en').Defaults.create_tokenizer()


@pytest.fixture
def en_vocab():
    return util.load_lang_class('en').Defaults.create_vocab()


@pytest.fixture
def en_parser():
    return util.load_lang_class('en').Defaults.create_parser()


@pytest.fixture
def es_tokenizer():
    return util.load_lang_class('es').Defaults.create_tokenizer()


@pytest.fixture
def de_tokenizer():
    return util.load_lang_class('de').Defaults.create_tokenizer()


@pytest.fixture(scope='module')
def fr_tokenizer():
    return util.load_lang_class('fr').Defaults.create_tokenizer()


@pytest.fixture
def hu_tokenizer():
    return util.load_lang_class('hu').Defaults.create_tokenizer()


@pytest.fixture
def fi_tokenizer():
    return util.load_lang_class('fi').Defaults.create_tokenizer()


@pytest.fixture
def sv_tokenizer():
    return util.load_lang_class('sv').Defaults.create_tokenizer()


@pytest.fixture
def bn_tokenizer():
    return util.load_lang_class('bn').Defaults.create_tokenizer()


@pytest.fixture
def he_tokenizer():
    return util.load_lang_class('he').Defaults.create_tokenizer()

@pytest.fixture
def nb_tokenizer():
    return util.load_lang_class('nb').Defaults.create_tokenizer()


@pytest.fixture
def stringstore():
    return StringStore()


@pytest.fixture
def en_entityrecognizer():
     return util.load_lang_class('en').Defaults.create_entity()


@pytest.fixture
def lemmatizer():
    return util.load_lang_class('en').Defaults.create_lemmatizer()


@pytest.fixture
def text_file():
    return StringIO()

@pytest.fixture
def text_file_b():
    return BytesIO()


# only used for tests that require loading the models
# in all other cases, use specific instances
@pytest.fixture(scope="session")
def EN():
    return English()


@pytest.fixture(scope="session")
def DE():
    return German()

@pytest.fixture(scope="session")
def FR():
    return French()


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
