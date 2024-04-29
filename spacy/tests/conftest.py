import pytest
from hypothesis import settings

from spacy.util import get_lang_class

# Functionally disable deadline settings for tests
# to prevent spurious test failures in CI builds.
settings.register_profile("no_deadlines", deadline=2 * 60 * 1000)  # in ms
settings.load_profile("no_deadlines")


def pytest_addoption(parser):
    try:
        parser.addoption("--slow", action="store_true", help="include slow tests")
        parser.addoption("--issue", action="store", help="test specific issues")
    # Options are already added, e.g. if conftest is copied in a build pipeline
    # and runs twice
    except ValueError:
        pass


def pytest_runtest_setup(item):
    def getopt(opt):
        # When using 'pytest --pyargs spacy' to test an installed copy of
        # spacy, pytest skips running our pytest_addoption() hook. Later, when
        # we call getoption(), pytest raises an error, because it doesn't
        # recognize the option we're asking about. To avoid this, we need to
        # pass a default value. We default to False, i.e., we act like all the
        # options weren't given.
        return item.config.getoption(f"--{opt}", False)

    # Integration of boolean flags
    for opt in ["slow"]:
        if opt in item.keywords and not getopt(opt):
            pytest.skip(f"need --{opt} option to run")

    # Special integration to mark tests with issue numbers
    issues = getopt("issue")
    if isinstance(issues, str):
        if "issue" in item.keywords:
            # Convert issues provided on the CLI to list of ints
            issue_nos = [int(issue.strip()) for issue in issues.split(",")]
            # Get all issues specified by decorators and check if they're provided
            issue_refs = [mark.args[0] for mark in item.iter_markers(name="issue")]
            if not any([ref in issue_nos for ref in issue_refs]):
                pytest.skip(f"not referencing specified issues: {issue_nos}")
        else:
            pytest.skip("not referencing any issues")


# Fixtures for language tokenizers (languages sorted alphabetically)


@pytest.fixture(scope="module")
def tokenizer():
    return get_lang_class("xx")().tokenizer


@pytest.fixture(scope="session")
def af_tokenizer():
    return get_lang_class("af")().tokenizer


@pytest.fixture(scope="session")
def am_tokenizer():
    return get_lang_class("am")().tokenizer


@pytest.fixture(scope="session")
def ar_tokenizer():
    return get_lang_class("ar")().tokenizer


@pytest.fixture(scope="session")
def bg_tokenizer():
    return get_lang_class("bg")().tokenizer


@pytest.fixture(scope="session")
def bn_tokenizer():
    return get_lang_class("bn")().tokenizer


@pytest.fixture(scope="session")
def ca_tokenizer():
    return get_lang_class("ca")().tokenizer


@pytest.fixture(scope="session")
def cs_tokenizer():
    return get_lang_class("cs")().tokenizer


@pytest.fixture(scope="session")
def da_tokenizer():
    return get_lang_class("da")().tokenizer


@pytest.fixture(scope="session")
def de_tokenizer():
    return get_lang_class("de")().tokenizer


@pytest.fixture(scope="session")
def de_vocab():
    return get_lang_class("de")().vocab


@pytest.fixture(scope="session")
def dsb_tokenizer():
    return get_lang_class("dsb")().tokenizer


@pytest.fixture(scope="session")
def el_tokenizer():
    return get_lang_class("el")().tokenizer


@pytest.fixture(scope="session")
def en_tokenizer():
    return get_lang_class("en")().tokenizer


@pytest.fixture(scope="session")
def en_vocab():
    return get_lang_class("en")().vocab


@pytest.fixture(scope="session")
def en_parser(en_vocab):
    nlp = get_lang_class("en")(en_vocab)
    return nlp.create_pipe("parser")


@pytest.fixture(scope="session")
def es_tokenizer():
    return get_lang_class("es")().tokenizer


@pytest.fixture(scope="session")
def es_vocab():
    return get_lang_class("es")().vocab


@pytest.fixture(scope="session")
def et_tokenizer():
    return get_lang_class("et")().tokenizer


@pytest.fixture(scope="session")
def eu_tokenizer():
    return get_lang_class("eu")().tokenizer


@pytest.fixture(scope="session")
def fa_tokenizer():
    return get_lang_class("fa")().tokenizer


@pytest.fixture(scope="session")
def fi_tokenizer():
    return get_lang_class("fi")().tokenizer


@pytest.fixture(scope="session")
def fo_tokenizer():
    return get_lang_class("fo")().tokenizer


@pytest.fixture(scope="session")
def fr_tokenizer():
    return get_lang_class("fr")().tokenizer


@pytest.fixture(scope="session")
def fr_vocab():
    return get_lang_class("fr")().vocab


@pytest.fixture(scope="session")
def ga_tokenizer():
    return get_lang_class("ga")().tokenizer


@pytest.fixture(scope="session")
def grc_tokenizer():
    return get_lang_class("grc")().tokenizer


@pytest.fixture(scope="session")
def gu_tokenizer():
    return get_lang_class("gu")().tokenizer


@pytest.fixture(scope="session")
def he_tokenizer():
    return get_lang_class("he")().tokenizer


@pytest.fixture(scope="session")
def hi_tokenizer():
    return get_lang_class("hi")().tokenizer


@pytest.fixture(scope="session")
def hr_tokenizer():
    return get_lang_class("hr")().tokenizer


@pytest.fixture
def hu_tokenizer():
    return get_lang_class("hu")().tokenizer


@pytest.fixture(scope="session")
def id_tokenizer():
    return get_lang_class("id")().tokenizer


@pytest.fixture(scope="session")
def is_tokenizer():
    return get_lang_class("is")().tokenizer


@pytest.fixture(scope="session")
def it_tokenizer():
    return get_lang_class("it")().tokenizer


@pytest.fixture(scope="session")
def it_vocab():
    return get_lang_class("it")().vocab


@pytest.fixture(scope="session")
def ja_tokenizer():
    pytest.importorskip("sudachipy")
    return get_lang_class("ja")().tokenizer


@pytest.fixture(scope="session")
def hsb_tokenizer():
    return get_lang_class("hsb")().tokenizer


@pytest.fixture(scope="session")
def ko_tokenizer():
    pytest.importorskip("natto")
    return get_lang_class("ko")().tokenizer


@pytest.fixture(scope="session")
def ko_tokenizer_tokenizer():
    config = {
        "nlp": {
            "tokenizer": {
                "@tokenizers": "spacy.Tokenizer.v1",
            }
        }
    }
    nlp = get_lang_class("ko").from_config(config)
    return nlp.tokenizer


@pytest.fixture(scope="module")
def la_tokenizer():
    return get_lang_class("la")().tokenizer


@pytest.fixture(scope="session")
def lb_tokenizer():
    return get_lang_class("lb")().tokenizer


@pytest.fixture(scope="session")
def lg_tokenizer():
    return get_lang_class("lg")().tokenizer


@pytest.fixture(scope="session")
def lt_tokenizer():
    return get_lang_class("lt")().tokenizer


@pytest.fixture(scope="session")
def lv_tokenizer():
    return get_lang_class("lv")().tokenizer


@pytest.fixture(scope="session")
def mk_tokenizer():
    return get_lang_class("mk")().tokenizer


@pytest.fixture(scope="session")
def ml_tokenizer():
    return get_lang_class("ml")().tokenizer


@pytest.fixture(scope="session")
def ms_tokenizer():
    return get_lang_class("ms")().tokenizer


@pytest.fixture(scope="session")
def nb_tokenizer():
    return get_lang_class("nb")().tokenizer


@pytest.fixture(scope="session")
def ne_tokenizer():
    return get_lang_class("ne")().tokenizer


@pytest.fixture(scope="session")
def nl_vocab():
    return get_lang_class("nl")().vocab


@pytest.fixture(scope="session")
def nl_tokenizer():
    return get_lang_class("nl")().tokenizer


@pytest.fixture(scope="session")
def nn_tokenizer():
    return get_lang_class("nn")().tokenizer


@pytest.fixture(scope="session")
def pl_tokenizer():
    return get_lang_class("pl")().tokenizer


@pytest.fixture(scope="session")
def pt_tokenizer():
    return get_lang_class("pt")().tokenizer


@pytest.fixture(scope="session")
def pt_vocab():
    return get_lang_class("pt")().vocab


@pytest.fixture(scope="session")
def ro_tokenizer():
    return get_lang_class("ro")().tokenizer


@pytest.fixture(scope="session")
def ru_tokenizer():
    pytest.importorskip("pymorphy3")
    return get_lang_class("ru")().tokenizer


@pytest.fixture(scope="session")
def ru_lemmatizer():
    pytest.importorskip("pymorphy3")
    return get_lang_class("ru")().add_pipe("lemmatizer")


@pytest.fixture(scope="session")
def ru_lookup_lemmatizer():
    pytest.importorskip("pymorphy3")
    return get_lang_class("ru")().add_pipe(
        "lemmatizer", config={"mode": "pymorphy3_lookup"}
    )


@pytest.fixture(scope="session")
def sa_tokenizer():
    return get_lang_class("sa")().tokenizer


@pytest.fixture(scope="session")
def sk_tokenizer():
    return get_lang_class("sk")().tokenizer


@pytest.fixture(scope="session")
def sl_tokenizer():
    return get_lang_class("sl")().tokenizer


@pytest.fixture(scope="session")
def sr_tokenizer():
    return get_lang_class("sr")().tokenizer


@pytest.fixture(scope="session")
def sq_tokenizer():
    return get_lang_class("sq")().tokenizer


@pytest.fixture(scope="session")
def sv_tokenizer():
    return get_lang_class("sv")().tokenizer


@pytest.fixture(scope="session")
def ta_tokenizer():
    return get_lang_class("ta")().tokenizer


@pytest.fixture(scope="session")
def th_tokenizer():
    pytest.importorskip("pythainlp")
    return get_lang_class("th")().tokenizer


@pytest.fixture(scope="session")
def ti_tokenizer():
    return get_lang_class("ti")().tokenizer


@pytest.fixture(scope="session")
def tl_tokenizer():
    return get_lang_class("tl")().tokenizer


@pytest.fixture(scope="session")
def tr_tokenizer():
    return get_lang_class("tr")().tokenizer


@pytest.fixture(scope="session")
def tt_tokenizer():
    return get_lang_class("tt")().tokenizer


@pytest.fixture(scope="session")
def ky_tokenizer():
    return get_lang_class("ky")().tokenizer


@pytest.fixture(scope="session")
def uk_tokenizer():
    pytest.importorskip("pymorphy3")
    return get_lang_class("uk")().tokenizer


@pytest.fixture(scope="session")
def uk_lemmatizer():
    pytest.importorskip("pymorphy3")
    pytest.importorskip("pymorphy3_dicts_uk")
    return get_lang_class("uk")().add_pipe("lemmatizer")


@pytest.fixture(scope="session")
def uk_lookup_lemmatizer():
    pytest.importorskip("pymorphy3")
    pytest.importorskip("pymorphy3_dicts_uk")
    return get_lang_class("uk")().add_pipe(
        "lemmatizer", config={"mode": "pymorphy3_lookup"}
    )


@pytest.fixture(scope="session")
def ur_tokenizer():
    return get_lang_class("ur")().tokenizer


@pytest.fixture(scope="session")
def vi_tokenizer():
    pytest.importorskip("pyvi")
    return get_lang_class("vi")().tokenizer


@pytest.fixture(scope="session")
def xx_tokenizer():
    return get_lang_class("xx")().tokenizer


@pytest.fixture(scope="session")
def yo_tokenizer():
    return get_lang_class("yo")().tokenizer


@pytest.fixture(scope="session")
def zh_tokenizer_char():
    nlp = get_lang_class("zh")()
    return nlp.tokenizer


@pytest.fixture(scope="session")
def zh_tokenizer_jieba():
    pytest.importorskip("jieba")
    config = {
        "nlp": {
            "tokenizer": {
                "@tokenizers": "spacy.zh.ChineseTokenizer",
                "segmenter": "jieba",
            }
        }
    }
    nlp = get_lang_class("zh").from_config(config)
    return nlp.tokenizer


@pytest.fixture(scope="session")
def zh_tokenizer_pkuseg():
    pytest.importorskip("spacy_pkuseg")
    config = {
        "nlp": {
            "tokenizer": {
                "@tokenizers": "spacy.zh.ChineseTokenizer",
                "segmenter": "pkuseg",
            }
        },
        "initialize": {"tokenizer": {"pkuseg_model": "web"}},
    }
    nlp = get_lang_class("zh").from_config(config)
    nlp.initialize()
    return nlp.tokenizer


@pytest.fixture(scope="session")
def hy_tokenizer():
    return get_lang_class("hy")().tokenizer
