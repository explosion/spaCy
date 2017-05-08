# coding: utf8
from __future__ import unicode_literals

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .stop_words import STOP_WORDS
from .morph_rules import MORPH_RULES

from ..language_data import BASE_EXCEPTIONS
from ..language import Language
from ..attrs import LANG
from ..util import update_exc


class Norwegian(Language):
    lang = 'nb'

    class Defaults(Language.Defaults):
        lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
        lex_attr_getters[LANG] = lambda text: 'nb'

        tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)
        stop_words = set(STOP_WORDS)


__all__ = ['Norwegian']
