# coding: utf-8
from __future__ import unicode_literals

from io import StringIO, BytesIO
from pathlib import Path
import pytest

from .util import load_test_model
from ..tokens import Doc
from ..strings import StringStore
from .. import util


# These languages are used for generic tokenizer tests – only add a language
# here if it's using spaCy's tokenizer (not a different library)
# TODO: re-implement generic tokenizer tests
_languages = ['bn', 'da', 'de', 'el', 'en', 'es', 'fi', 'fr', 'ga', 'he', 'hu', 'id',
              'it', 'nb', 'nl', 'pl', 'pt', 'ro', 'ru', 'sv', 'tr', 'ar', 'ut', 'tt',
              'xx']

_models = {'en': ['en_core_web_sm'],
           'de': ['de_core_news_sm'],
           'fr': ['fr_core_news_sm'],
           'xx': ['xx_ent_web_sm'],
           'en_core_web_md': ['en_core_web_md'],
           'es_core_news_md': ['es_core_news_md']}


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


@pytest.fixture()
def RU(request):
    pymorphy = pytest.importorskip('pymorphy2')
    return util.get_lang_class('ru')()

@pytest.fixture()
def JA(request):
    mecab = pytest.importorskip("MeCab")
    return util.get_lang_class('ja')()


#@pytest.fixture(params=_languages)
#def tokenizer(request):
#lang = util.get_lang_class(request.param)
#return lang.Defaults.create_tokenizer()


@pytest.fixture
def tokenizer():
    return util.get_lang_class('xx').Defaults.create_tokenizer()


@pytest.fixture(scope='session')
def en_tokenizer():
    return util.get_lang_class('en').Defaults.create_tokenizer()


@pytest.fixture
def en_vocab():
    return util.get_lang_class('en').Defaults.create_vocab()


@pytest.fixture
def en_parser(en_vocab):
    nlp = util.get_lang_class('en')(en_vocab)
    return nlp.create_pipe('parser')


@pytest.fixture(scope='session')
def es_tokenizer():
    return util.get_lang_class('es').Defaults.create_tokenizer()


@pytest.fixture(scope='session')
def de_tokenizer():
    return util.get_lang_class('de').Defaults.create_tokenizer()


@pytest.fixture(scope='session')
def hu_tokenizer():
    return util.get_lang_class('hu').Defaults.create_tokenizer()


@pytest.fixture(scope='session')
def fi_tokenizer():
    return util.get_lang_class('fi').Defaults.create_tokenizer()


@pytest.fixture(scope='session')
def ro_tokenizer():
    return util.get_lang_class('ro').Defaults.create_tokenizer()


@pytest.fixture(scope='session')
def id_tokenizer():
    return util.get_lang_class('id').Defaults.create_tokenizer()


@pytest.fixture(scope='session')
def sv_tokenizer():
    return util.get_lang_class('sv').Defaults.create_tokenizer()


@pytest.fixture(scope='session')
def bn_tokenizer():
    return util.get_lang_class('bn').Defaults.create_tokenizer()


@pytest.fixture(scope='session')
def ga_tokenizer():
    return util.get_lang_class('ga').Defaults.create_tokenizer()


@pytest.fixture(scope='session')
def he_tokenizer():
    return util.get_lang_class('he').Defaults.create_tokenizer()


@pytest.fixture(scope='session')
def nb_tokenizer():
    return util.get_lang_class('nb').Defaults.create_tokenizer()

@pytest.fixture(scope='session')
def da_tokenizer():
    return util.get_lang_class('da').Defaults.create_tokenizer()

@pytest.fixture(scope='session')
def ja_tokenizer():
    mecab = pytest.importorskip("MeCab")
    return util.get_lang_class('ja').Defaults.create_tokenizer()

@pytest.fixture(scope='session')
def th_tokenizer():
    pythainlp = pytest.importorskip("pythainlp")
    return util.get_lang_class('th').Defaults.create_tokenizer()

@pytest.fixture(scope='session')
def tr_tokenizer():
    return util.get_lang_class('tr').Defaults.create_tokenizer()

@pytest.fixture(scope='session')
def tt_tokenizer():
    return util.get_lang_class('tt').Defaults.create_tokenizer()

@pytest.fixture(scope='session')
def el_tokenizer():
    return util.get_lang_class('el').Defaults.create_tokenizer()

@pytest.fixture(scope='session')
def ar_tokenizer():
    return util.get_lang_class('ar').Defaults.create_tokenizer()

@pytest.fixture(scope='session')
def ur_tokenizer():
    return util.get_lang_class('ur').Defaults.create_tokenizer()

@pytest.fixture(scope='session')
def ru_tokenizer():
    pymorphy = pytest.importorskip('pymorphy2')
    return util.get_lang_class('ru').Defaults.create_tokenizer()


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
    for model in _models:
        if model not in _languages:
            parser.addoption("--%s" % model, action="store_true", help="Use %s model" % model)


def pytest_runtest_setup(item):
    def getopt(opt):
        # When using 'pytest --pyargs spacy' to test an installed copy of
        # spacy, pytest skips running our pytest_addoption() hook. Later, when
        # we call getoption(), pytest raises an error, because it doesn't
        # recognize the option we're asking about. To avoid this, we need to
        # pass a default value. We default to False, i.e., we act like all the
        # options weren't given.
        return item.config.getoption("--%s" % opt, False)

    for opt in ['models', 'vectors', 'slow']:
        if opt in item.keywords and not getopt(opt):
            pytest.skip("need --%s option to run" % opt)

    # Check if test is marked with models and has arguments set, i.e. specific
    # language. If so, skip test if flag not set.
    if item.get_marker('models'):
        for arg in item.get_marker('models').args:
            if not getopt(arg) and not getopt("all"):
                pytest.skip("need --%s or --all option to run" % arg)
