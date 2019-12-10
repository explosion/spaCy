# coding: utf8
from __future__ import unicode_literals

from .stop_words import STOP_WORDS
from .punctuation import TOKENIZER_SUFFIXES, TOKENIZER_PREFIXES, TOKENIZER_INFIXES
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .norm_exceptions import NORM_EXCEPTIONS
from .lex_attrs import LEX_ATTRS
from .syntax_iterators import SYNTAX_ITERATORS
from .tag_map import TAG_MAP

from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ..norm_exceptions import BASE_NORMS
from ...language import Language
from ...attrs import LANG, NORM
from ...util import update_exc, add_lookups


class IndonesianDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters[LANG] = lambda text: "id"
    lex_attr_getters.update(LEX_ATTRS)
    lex_attr_getters[NORM] = add_lookups(
        Language.Defaults.lex_attr_getters[NORM], BASE_NORMS, NORM_EXCEPTIONS
    )
    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)
    stop_words = STOP_WORDS
    prefixes = TOKENIZER_PREFIXES
    suffixes = TOKENIZER_SUFFIXES
    infixes = TOKENIZER_INFIXES
    syntax_iterators = SYNTAX_ITERATORS
    tag_map = TAG_MAP


class Indonesian(Language):
    lang = "id"
    Defaults = IndonesianDefaults


__all__ = ["Indonesian"]
