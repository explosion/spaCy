from thinc.api import Config

from .punctuation import TOKENIZER_PREFIXES, TOKENIZER_INFIXES
from .punctuation import TOKENIZER_SUFFIXES
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from .lemmatizer import PolishLemmatizer
from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ..norm_exceptions import BASE_NORMS
from ...language import Language
from ...attrs import LANG, NORM
from ...util import add_lookups, registry


DEFAULT_CONFIG = """
[nlp]
lang = "pl"

[nlp.lemmatizer]
@lemmatizers = "spacy.PolishLemmatizer.v1"
data_paths = {"@lookups": "spacy-lookups-data.pl"}
"""


@registry.lemmatizers("spacy.PolishLemmatizer.v1")
def create_polish_lemmatizer(data_paths: dict = {}) -> PolishLemmatizer:
    return PolishLemmatizer(data_paths=data_paths)


class PolishDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters.update(LEX_ATTRS)
    lex_attr_getters[LANG] = lambda text: "pl"
    lex_attr_getters[NORM] = add_lookups(
        Language.Defaults.lex_attr_getters[NORM], BASE_NORMS
    )
    mod_base_exceptions = {
        exc: val for exc, val in BASE_EXCEPTIONS.items() if not exc.endswith(".")
    }
    tokenizer_exceptions = mod_base_exceptions
    stop_words = STOP_WORDS
    prefixes = TOKENIZER_PREFIXES
    infixes = TOKENIZER_INFIXES
    suffixes = TOKENIZER_SUFFIXES


class Polish(Language):
    lang = "pl"
    Defaults = PolishDefaults
    default_config = Config().from_str(DEFAULT_CONFIG)


__all__ = ["Polish"]
