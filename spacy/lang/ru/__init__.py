# encoding: utf8
from __future__ import unicode_literals, print_function

from .stop_words import STOP_WORDS
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .norm_exceptions import NORM_EXCEPTIONS
from .lex_attrs import LEX_ATTRS
from .tag_map import TAG_MAP
from .lemmatizer import RussianLemmatizer

from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ..norm_exceptions import BASE_NORMS
from ...util import update_exc, add_lookups
from ...language import Language
from ...attrs import LANG, NORM


class RussianDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters.update(LEX_ATTRS)
    lex_attr_getters[LANG] = lambda text: "ru"
    lex_attr_getters[NORM] = add_lookups(
        Language.Defaults.lex_attr_getters[NORM], BASE_NORMS, NORM_EXCEPTIONS
    )
    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)
    stop_words = STOP_WORDS
    tag_map = TAG_MAP

    @classmethod
    def create_lemmatizer(cls, nlp=None):
        return RussianLemmatizer()


class Russian(Language):
    lang = "ru"
    Defaults = RussianDefaults


__all__ = ["Russian"]
