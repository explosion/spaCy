# coding: utf-8
from __future__ import unicode_literals

import pytest
from io import StringIO, BytesIO
from spacy.util import get_lang_class


def pytest_addoption(parser):
    parser.addoption("--slow", action="store_true", help="include slow tests")


def pytest_runtest_setup(item):
    for opt in ['slow']:
        if opt in item.keywords and not item.config.getoption("--%s" % opt):
            pytest.skip("need --%s option to run" % opt)


@pytest.fixture(scope='module')
def tokenizer():
    return get_lang_class('xx').Defaults.create_tokenizer()


@pytest.fixture(scope='session')
def en_tokenizer():
    return get_lang_class('en').Defaults.create_tokenizer()


@pytest.fixture(scope='session')
def en_vocab():
    return get_lang_class('en').Defaults.create_vocab()


@pytest.fixture(scope='session')
def en_parser(en_vocab):
    nlp = get_lang_class('en')(en_vocab)
    return nlp.create_pipe('parser')


@pytest.fixture(scope='session')
def es_tokenizer():
    return get_lang_class('es').Defaults.create_tokenizer()


@pytest.fixture(scope='session')
def de_tokenizer():
    return get_lang_class('de').Defaults.create_tokenizer()


@pytest.fixture(scope='session')
def fr_tokenizer():
    return get_lang_class('fr').Defaults.create_tokenizer()


@pytest.fixture
def hu_tokenizer():
    return get_lang_class('hu').Defaults.create_tokenizer()


@pytest.fixture(scope='session')
def fi_tokenizer():
    return get_lang_class('fi').Defaults.create_tokenizer()


@pytest.fixture(scope='session')
def ro_tokenizer():
    return get_lang_class('ro').Defaults.create_tokenizer()


@pytest.fixture(scope='session')
def id_tokenizer():
    return get_lang_class('id').Defaults.create_tokenizer()


@pytest.fixture(scope='session')
def sv_tokenizer():
    return get_lang_class('sv').Defaults.create_tokenizer()


@pytest.fixture(scope='session')
def bn_tokenizer():
    return get_lang_class('bn').Defaults.create_tokenizer()


@pytest.fixture(scope='session')
def ga_tokenizer():
    return get_lang_class('ga').Defaults.create_tokenizer()


@pytest.fixture(scope='session')
def he_tokenizer():
    return get_lang_class('he').Defaults.create_tokenizer()


@pytest.fixture(scope='session')
def nb_tokenizer():
    return get_lang_class('nb').Defaults.create_tokenizer()

@pytest.fixture(scope='session')
def da_tokenizer():
    return get_lang_class('da').Defaults.create_tokenizer()

@pytest.fixture(scope='session')
def ja_tokenizer():
    mecab = pytest.importorskip("MeCab")
    return get_lang_class('ja').Defaults.create_tokenizer()

@pytest.fixture(scope='session')
def th_tokenizer():
    pythainlp = pytest.importorskip("pythainlp")
    return get_lang_class('th').Defaults.create_tokenizer()

@pytest.fixture(scope='session')
def tr_tokenizer():
    return get_lang_class('tr').Defaults.create_tokenizer()

@pytest.fixture(scope='session')
def tt_tokenizer():
    return get_lang_class('tt').Defaults.create_tokenizer()

@pytest.fixture(scope='session')
def el_tokenizer():
    return get_lang_class('el').Defaults.create_tokenizer()

@pytest.fixture(scope='session')
def ar_tokenizer():
    return get_lang_class('ar').Defaults.create_tokenizer()

@pytest.fixture(scope='session')
def ur_tokenizer():
    return get_lang_class('ur').Defaults.create_tokenizer()

@pytest.fixture(scope='session')
def ru_tokenizer():
    pymorphy = pytest.importorskip('pymorphy2')
    return get_lang_class('ru').Defaults.create_tokenizer()
