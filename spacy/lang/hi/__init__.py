# coding: utf8
from __future__ import unicode_literals

from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS

from ..norm_exceptions import BASE_NORMS
from ...language import Language
from ...attrs import LANG


class HindiDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    # overwrite functions for lexical attributes
    lex_attr_getters.update(LEX_ATTRS)
    lex_attr_getters[LANG] = lambda text: 'hi'
    # add stop words
    stop_words = STOP_WORDS
    # add more norm exception dictionaries here
    # lex_attr_getters[NORM] = add_lookups(Language.Defaults.lex_attr_getters[NORM], BASE_NORMS)
    # add custom tokenizer exceptions to base exceptions
    # tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)
    # if available: add tag map
    # tag_map = dict(TAG_MAP)

    # if available: add morph rules
    # morph_rules = dict(MORPH_RULES)

    # if available: add lookup lemmatizer
    # @classmethod
    # def create_lemmatizer(cls, nlp=None):
    #     return Lemmatizer(LOOKUP)


class Hindi(Language):
    lang = 'hi'
    Defaults = HindiDefaults


__all__ = ['Hindi']
