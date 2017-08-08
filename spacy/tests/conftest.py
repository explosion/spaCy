# coding: utf-8
from __future__ import unicode_literals

from io import StringIO, BytesIO
from pathlib import Path
import pytest

from .util import load_test_model
from ..tokens import Doc
from ..strings import StringStore
from .. import util


_languages = ['bn', 'da', 'de', 'en', 'es', 'fi', 'fr', 'he', 'hu', 'it', 'nb',
              'nl', 'pl', 'pt', 'sv', 'xx']
_models = {'en': ['en_depent_web_sm', 'en_core_web_md'],
           'de': ['de_core_news_md'],
           'fr': ['fr_depvec_web_lg'],
           'xx': ['xx_ent_web_md']}


# only used for tests that require loading the models
# in all other cases, use specific instances

@pytest.fixture(params=_models['en'])
def EN(request):
    return load_test_model(request.param)


@pytest.fixture(params=_models['de'])
def DE(request):
    return load_test_model(request.param)


@pytest.fixture(params=_models['fr'])
def FR(request):
    return load_test_model(request.param)


#@pytest.fixture(params=_languages)
#def tokenizer(request):
    #lang = util.get_lang_class(request.param)
    #return lang.Defaults.create_tokenizer()

@pytest.fixture
def tokenizer():
    return util.get_lang_class('xx').Defaults.create_tokenizer()


@pytest.fixture
def en_tokenizer():
    return util.get_lang_class('en').Defaults.create_tokenizer()


@pytest.fixture
def en_vocab():
    return util.get_lang_class('en').Defaults.create_vocab()


@pytest.fixture
def en_parser():
    return util.get_lang_class('en').Defaults.create_parser()


@pytest.fixture
def es_tokenizer():
    return util.get_lang_class('es').Defaults.create_tokenizer()


@pytest.fixture
def de_tokenizer():
    return util.get_lang_class('de').Defaults.create_tokenizer()


@pytest.fixture
def fr_tokenizer():
    return util.get_lang_class('fr').Defaults.create_tokenizer()


@pytest.fixture
def hu_tokenizer():
    return util.get_lang_class('hu').Defaults.create_tokenizer()


@pytest.fixture
def fi_tokenizer():
    return util.get_lang_class('fi').Defaults.create_tokenizer()


@pytest.fixture
def sv_tokenizer():
    return util.get_lang_class('sv').Defaults.create_tokenizer()


@pytest.fixture
def bn_tokenizer():
    return util.get_lang_class('bn').Defaults.create_tokenizer()


@pytest.fixture
def he_tokenizer():
    return util.get_lang_class('he').Defaults.create_tokenizer()

@pytest.fixture
def nb_tokenizer():
    return util.get_lang_class('nb').Defaults.create_tokenizer()


@pytest.fixture
def stringstore():
    return StringStore()


@pytest.fixture
def en_entityrecognizer():
     return util.get_lang_class('en').Defaults.create_entity()


@pytest.fixture
def text_file():
    return StringIO()

@pytest.fixture
def text_file_b():
    return BytesIO()


def pytest_addoption(parser):
    parser.addoption("--models", action="store_true",
        help="include tests that require full models")
    parser.addoption("--vectors", action="store_true",
        help="include word vectors tests")
    parser.addoption("--slow", action="store_true",
        help="include slow tests")

    for lang in _languages + ['all']:
        parser.addoption("--%s" % lang, action="store_true", help="Use %s models" % lang)


def pytest_runtest_setup(item):
    for opt in ['models', 'vectors', 'slow']:
        if opt in item.keywords and not item.config.getoption("--%s" % opt):
            pytest.skip("need --%s option to run" % opt)

    # Check if test is marked with models and has arguments set, i.e. specific
    # language. If so, skip test if flag not set.
    if item.get_marker('models'):
        for arg in item.get_marker('models').args:
            if not item.config.getoption("--%s" % arg) and not item.config.getoption("--all"):
                pytest.skip("need --%s or --all option to run" % arg)
