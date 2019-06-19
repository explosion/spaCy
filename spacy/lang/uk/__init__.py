# coding: utf8
from __future__ import unicode_literals

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS

from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ..norm_exceptions import BASE_NORMS
from ...util import update_exc, add_lookups
from ...language import Language
from ...attrs import LANG, NORM
from .lemmatizer import UkrainianLemmatizer


class UkrainianDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters[LANG] = lambda text: "uk"
    lex_attr_getters[NORM] = add_lookups(
        Language.Defaults.lex_attr_getters[NORM], BASE_NORMS
    )
    lex_attr_getters.update(LEX_ATTRS)
    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)
    stop_words = STOP_WORDS

    @classmethod
    def create_lemmatizer(cls, nlp=None):
        return UkrainianLemmatizer()


class Ukrainian(Language):
    lang = "uk"
    Defaults = UkrainianDefaults


__all__ = ["Ukrainian"]
