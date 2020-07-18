from thinc.api import Config

from .stop_words import STOP_WORDS
from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ...language import Language
from ...attrs import LANG
from ...util import update_exc


DEFAULT_CONFIG = """
[nlp]
lang = "he"

[nlp.writing_system]
direction = "rtl"
has_case = false
has_letters = true
"""


class HebrewDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters[LANG] = lambda text: "he"
    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS)
    stop_words = STOP_WORDS


class Hebrew(Language):
    lang = "he"
    Defaults = HebrewDefaults
    default_config = Config().from_str(DEFAULT_CONFIG)


__all__ = ["Hebrew"]
