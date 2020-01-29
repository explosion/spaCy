from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .stop_words import STOP_WORDS
from .tag_map import TAG_MAP

from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ...language import Language
from ...attrs import LANG
from ...util import update_exc


class IrishDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters[LANG] = lambda text: "ga"

    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)
    stop_words = set(STOP_WORDS)
    tag_map = TAG_MAP


class Irish(Language):
    lang = "ga"
    Defaults = IrishDefaults


__all__ = ["Irish"]
