from thinc.api import Config

from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from .tag_map import TAG_MAP
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .punctuation import TOKENIZER_PREFIXES, TOKENIZER_INFIXES
from .punctuation import TOKENIZER_SUFFIXES
from .lemmatizer import DutchLemmatizer
from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ..norm_exceptions import BASE_NORMS
from ...language import Language
from ...attrs import LANG, NORM
from ...util import update_exc, add_lookups, registry


DEFAULT_CONFIG = """
[nlp]
lang = "nl"

[nlp.lemmatizer]
@lemmatizers = "spacy.DutchLemmatizer.v1"
data_paths = {"@lookups": "spacy-lookups-data.nl"}
"""


@registry.lemmatizers("spacy.DutchLemmatizer.v1")
def create_dutch_lemmatizer(data_paths: dict = {}) -> DutchLemmatizer:
    return DutchLemmatizer(data_paths=data_paths)


class DutchDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters.update(LEX_ATTRS)
    lex_attr_getters[LANG] = lambda text: "nl"
    lex_attr_getters[NORM] = add_lookups(
        Language.Defaults.lex_attr_getters[NORM], BASE_NORMS
    )
    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)
    stop_words = STOP_WORDS
    tag_map = TAG_MAP
    prefixes = TOKENIZER_PREFIXES
    infixes = TOKENIZER_INFIXES
    suffixes = TOKENIZER_SUFFIXES


class Dutch(Language):
    lang = "nl"
    Defaults = DutchDefaults
    default_config = Config().from_str(DEFAULT_CONFIG)


__all__ = ["Dutch"]
