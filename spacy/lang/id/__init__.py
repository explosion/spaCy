# coding: utf8
from __future__ import unicode_literals

from .stop_words import STOP_WORDS
from .punctuation import TOKENIZER_SUFFIXES, TOKENIZER_PREFIXES, TOKENIZER_INFIXES
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .norm_exceptions import NORM_EXCEPTIONS
from .lemmatizer import LOOKUP
from .lex_attrs import LEX_ATTRS
from .syntax_iterators import SYNTAX_ITERATORS

from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ...language import Language
from ...lemmatizerlookup import Lemmatizer
from ...attrs import LANG
from ...util import update_exc


class IndonesianDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters[LANG] = lambda text: 'id'

    lex_attr_getters.update(LEX_ATTRS)

    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)
    stop_words = set(STOP_WORDS)
    prefixes = tuple(TOKENIZER_PREFIXES)
    suffixes = tuple(TOKENIZER_SUFFIXES)
    infixes = tuple(TOKENIZER_INFIXES)
    syntax_iterators = dict(SYNTAX_ITERATORS)

    @classmethod
    def create_lemmatizer(cls, nlp=None):
        return Lemmatizer(LOOKUP)


class Indonesian(Language):
    lang = 'id'
    Defaults = IndonesianDefaults


__all__ = ['Indonesian']
