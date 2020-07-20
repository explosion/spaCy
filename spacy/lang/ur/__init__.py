from thinc.api import Config

from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from .punctuation import TOKENIZER_SUFFIXES
from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ...language import Language
from ...attrs import LANG


DEFAULT_CONFIG = """
[nlp]
lang = "ur"

[nlp.writing_system]
direction = "rtl"
has_case = false
has_letters = true

[nlp.lemmatizer]
@lemmatizers = "spacy.Lemmatizer.v1"

[nlp.lemmatizer.data_paths]
@assets = "spacy-lookups-data"
lang = ${nlp:lang}
"""


class UrduDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters.update(LEX_ATTRS)
    lex_attr_getters[LANG] = lambda text: "ur"
    tokenizer_exceptions = BASE_EXCEPTIONS
    stop_words = STOP_WORDS
    suffixes = TOKENIZER_SUFFIXES


class Urdu(Language):
    lang = "ur"
    Defaults = UrduDefaults
    default_config = Config().from_str(DEFAULT_CONFIG)


__all__ = ["Urdu"]
