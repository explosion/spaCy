from thinc.api import Config

from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from .punctuation import TOKENIZER_SUFFIXES

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ..norm_exceptions import BASE_NORMS
from ...language import Language
from ...attrs import LANG, NORM
from ...util import update_exc, add_lookups

DEFAULT_CONFIG = """
[nlp]
lang = "ar"

[nlp.writing_system]
direction = "rtl"
has_case = false
has_letters = true
"""


class ArabicDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters.update(LEX_ATTRS)
    lex_attr_getters[LANG] = lambda text: "ar"
    lex_attr_getters[NORM] = add_lookups(
        Language.Defaults.lex_attr_getters[NORM], BASE_NORMS
    )
    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)
    stop_words = STOP_WORDS
    suffixes = TOKENIZER_SUFFIXES


class Arabic(Language):
    lang = "ar"
    Defaults = ArabicDefaults
    default_config = Config().from_str(DEFAULT_CONFIG)


__all__ = ["Arabic"]
