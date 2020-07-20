from thinc.api import Config

from ...language import Language
from ...attrs import LANG, NORM
from ...util import update_exc, add_lookups
from ..norm_exceptions import BASE_NORMS
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .punctuation import TOKENIZER_SUFFIXES
from .syntax_iterators import SYNTAX_ITERATORS


DEFAULT_CONFIG = """
[nlp]
lang = "fa"

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


class PersianDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters.update(LEX_ATTRS)
    lex_attr_getters[NORM] = add_lookups(
        Language.Defaults.lex_attr_getters[NORM], BASE_NORMS
    )
    lex_attr_getters[LANG] = lambda text: "fa"
    tokenizer_exceptions = update_exc(TOKENIZER_EXCEPTIONS)
    stop_words = STOP_WORDS
    suffixes = TOKENIZER_SUFFIXES
    syntax_iterators = SYNTAX_ITERATORS


class Persian(Language):
    lang = "fa"
    Defaults = PersianDefaults
    default_config = Config().from_str(DEFAULT_CONFIG)


__all__ = ["Persian"]
