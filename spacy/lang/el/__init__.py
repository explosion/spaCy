# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from ..tag_map import TAG_MAP
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from .lemmatizer import GreekLemmatizer
from .syntax_iterators import SYNTAX_ITERATORS
from .punctuation import TOKENIZER_PREFIXES, TOKENIZER_SUFFIXES, TOKENIZER_INFIXES
from ..tokenizer_exceptions import BASE_EXCEPTIONS
from .norm_exceptions import NORM_EXCEPTIONS
from ..norm_exceptions import BASE_NORMS
from ...language import Language
from ...lookups import Lookups
from ...attrs import LANG, NORM
from ...util import update_exc, add_lookups


class GreekDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters.update(LEX_ATTRS)
    lex_attr_getters[LANG] = lambda text: "el"
    lex_attr_getters[NORM] = add_lookups(
        Language.Defaults.lex_attr_getters[NORM], BASE_NORMS, NORM_EXCEPTIONS
    )
    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)
    stop_words = STOP_WORDS
    tag_map = TAG_MAP
    prefixes = TOKENIZER_PREFIXES
    suffixes = TOKENIZER_SUFFIXES
    infixes = TOKENIZER_INFIXES
    syntax_iterators = SYNTAX_ITERATORS

    @classmethod
    def create_lemmatizer(cls, nlp=None, lookups=None):
        if lookups is None:
            lookups = Lookups()
        return GreekLemmatizer(lookups)


class Greek(Language):
    lang = "el"
    Defaults = GreekDefaults


__all__ = ["Greek"]
