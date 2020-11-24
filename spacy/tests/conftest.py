# coding: utf-8
from __future__ import unicode_literals

import pytest
from spacy.util import get_lang_class


def pytest_addoption(parser):
    parser.addoption("--slow", action="store_true", help="include slow tests")


def pytest_runtest_setup(item):
    def getopt(opt):
        # When using 'pytest --pyargs spacy' to test an installed copy of
        # spacy, pytest skips running our pytest_addoption() hook. Later, when
        # we call getoption(), pytest raises an error, because it doesn't
        # recognize the option we're asking about. To avoid this, we need to
        # pass a default value. We default to False, i.e., we act like all the
        # options weren't given.
        return item.config.getoption("--%s" % opt, False)

    for opt in ["slow"]:
        if opt in item.keywords and not getopt(opt):
            pytest.skip("need --%s option to run" % opt)


# Fixtures for language tokenizers (languages sorted alphabetically)


@pytest.fixture(scope="module")
def tokenizer():
    return get_lang_class("xx").Defaults.create_tokenizer()


@pytest.fixture(scope="session")
def ar_tokenizer():
    return get_lang_class("ar").Defaults.create_tokenizer()


@pytest.fixture(scope="session")
def bn_tokenizer():
    return get_lang_class("bn").Defaults.create_tokenizer()


@pytest.fixture(scope="session")
def ca_tokenizer():
    return get_lang_class("ca").Defaults.create_tokenizer()


@pytest.fixture(scope="session")
def cs_tokenizer():
    return get_lang_class("cs").Defaults.create_tokenizer()


@pytest.fixture(scope="session")
def da_tokenizer():
    return get_lang_class("da").Defaults.create_tokenizer()


@pytest.fixture(scope="session")
def de_tokenizer():
    return get_lang_class("de").Defaults.create_tokenizer()


@pytest.fixture(scope="session")
def el_tokenizer():
    return get_lang_class("el").Defaults.create_tokenizer()


@pytest.fixture(scope="session")
def en_tokenizer():
    return get_lang_class("en").Defaults.create_tokenizer()


@pytest.fixture(scope="session")
def en_vocab():
    return get_lang_class("en").Defaults.create_vocab()


@pytest.fixture(scope="session")
def en_parser(en_vocab):
    nlp = get_lang_class("en")(en_vocab)
    return nlp.create_pipe("parser")


@pytest.fixture(scope="session")
def es_tokenizer():
    return get_lang_class("es").Defaults.create_tokenizer()


@pytest.fixture(scope="session")
def eu_tokenizer():
    return get_lang_class("eu").Defaults.create_tokenizer()


@pytest.fixture(scope="session")
def fa_tokenizer():
    return get_lang_class("fa").Defaults.create_tokenizer()


@pytest.fixture(scope="session")
def fi_tokenizer():
    return get_lang_class("fi").Defaults.create_tokenizer()


@pytest.fixture(scope="session")
def fr_tokenizer():
    return get_lang_class("fr").Defaults.create_tokenizer()


@pytest.fixture(scope="session")
def ga_tokenizer():
    return get_lang_class("ga").Defaults.create_tokenizer()


@pytest.fixture(scope="session")
def gu_tokenizer():
    return get_lang_class("gu").Defaults.create_tokenizer()


@pytest.fixture(scope="session")
def he_tokenizer():
    return get_lang_class("he").Defaults.create_tokenizer()


@pytest.fixture(scope="session")
def hi_tokenizer():
    return get_lang_class("hi").Defaults.create_tokenizer()


@pytest.fixture(scope="session")
def hr_tokenizer():
    return get_lang_class("hr").Defaults.create_tokenizer()


@pytest.fixture
def hu_tokenizer():
    return get_lang_class("hu").Defaults.create_tokenizer()


@pytest.fixture(scope="session")
def id_tokenizer():
    return get_lang_class("id").Defaults.create_tokenizer()


@pytest.fixture(scope="session")
def it_tokenizer():
    return get_lang_class("it").Defaults.create_tokenizer()


@pytest.fixture(scope="session")
def ja_tokenizer():
    pytest.importorskip("sudachipy")
    return get_lang_class("ja").Defaults.create_tokenizer()


@pytest.fixture(scope="session")
def ko_tokenizer():
    pytest.importorskip("natto")
    return get_lang_class("ko").Defaults.create_tokenizer()


@pytest.fixture(scope="session")
def lb_tokenizer():
    return get_lang_class("lb").Defaults.create_tokenizer()


@pytest.fixture(scope="session")
def lt_tokenizer():
    return get_lang_class("lt").Defaults.create_tokenizer()


@pytest.fixture(scope="session")
def mk_tokenizer():
    return get_lang_class("mk").Defaults.create_tokenizer()


@pytest.fixture(scope="session")
def ml_tokenizer():
    return get_lang_class("ml").Defaults.create_tokenizer()


@pytest.fixture(scope="session")
def nb_tokenizer():
    return get_lang_class("nb").Defaults.create_tokenizer()


@pytest.fixture(scope="session")
def ne_tokenizer():
    return get_lang_class("ne").Defaults.create_tokenizer()


@pytest.fixture(scope="session")
def nl_tokenizer():
    return get_lang_class("nl").Defaults.create_tokenizer()


@pytest.fixture(scope="session")
def pl_tokenizer():
    return get_lang_class("pl").Defaults.create_tokenizer()


@pytest.fixture(scope="session")
def pt_tokenizer():
    return get_lang_class("pt").Defaults.create_tokenizer()


@pytest.fixture(scope="session")
def ro_tokenizer():
    return get_lang_class("ro").Defaults.create_tokenizer()


@pytest.fixture(scope="session")
def ru_tokenizer():
    pytest.importorskip("pymorphy2")
    return get_lang_class("ru").Defaults.create_tokenizer()


@pytest.fixture
def ru_lemmatizer():
    pytest.importorskip("pymorphy2")
    return get_lang_class("ru").Defaults.create_lemmatizer()


@pytest.fixture(scope="session")
def sa_tokenizer():
    return get_lang_class("sa").Defaults.create_tokenizer()


@pytest.fixture(scope="session")
def sr_tokenizer():
    return get_lang_class("sr").Defaults.create_tokenizer()


@pytest.fixture(scope="session")
def sv_tokenizer():
    return get_lang_class("sv").Defaults.create_tokenizer()


@pytest.fixture(scope="session")
def th_tokenizer():
    pytest.importorskip("pythainlp")
    return get_lang_class("th").Defaults.create_tokenizer()


@pytest.fixture(scope="session")
def tr_tokenizer():
    return get_lang_class("tr").Defaults.create_tokenizer()

@pytest.fixture(scope="session")
def tr_vocab():
    return get_lang_class("tr").Defaults.create_vocab()

@pytest.fixture(scope="session")
def tt_tokenizer():
    return get_lang_class("tt").Defaults.create_tokenizer()


@pytest.fixture(scope="session")
def uk_tokenizer():
    pytest.importorskip("pymorphy2")
    pytest.importorskip("pymorphy2.lang")
    return get_lang_class("uk").Defaults.create_tokenizer()


@pytest.fixture(scope="session")
def ur_tokenizer():
    return get_lang_class("ur").Defaults.create_tokenizer()


@pytest.fixture(scope="session")
def yo_tokenizer():
    return get_lang_class("yo").Defaults.create_tokenizer()


@pytest.fixture(scope="session")
def zh_tokenizer_char():
    return get_lang_class("zh").Defaults.create_tokenizer(
        config={"use_jieba": False, "use_pkuseg": False}
    )


@pytest.fixture(scope="session")
def zh_tokenizer_jieba():
    pytest.importorskip("jieba")
    return get_lang_class("zh").Defaults.create_tokenizer()


@pytest.fixture(scope="session")
def zh_tokenizer_pkuseg():
    pytest.importorskip("pkuseg")
    return get_lang_class("zh").Defaults.create_tokenizer(
        config={"pkuseg_model": "default", "use_jieba": False, "use_pkuseg": True}
    )


@pytest.fixture(scope="session")
def hy_tokenizer():
    return get_lang_class("hy").Defaults.create_tokenizer()
