# coding: utf8
from __future__ import unicode_literals

from ...language import Language
from ...attrs import LANG, NORM
from ...util import update_exc, add_lookups
from ..norm_exceptions import BASE_NORMS
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .tag_map import TAG_MAP
from .punctuation import TOKENIZER_SUFFIXES
from .syntax_iterators import SYNTAX_ITERATORS


class PersianDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters.update(LEX_ATTRS)
    lex_attr_getters[NORM] = add_lookups(
        Language.Defaults.lex_attr_getters[NORM], BASE_NORMS
    )
    lex_attr_getters[LANG] = lambda text: "fa"
    tokenizer_exceptions = update_exc(TOKENIZER_EXCEPTIONS)
    stop_words = STOP_WORDS
    tag_map = TAG_MAP
    suffixes = TOKENIZER_SUFFIXES
    writing_system = {"direction": "rtl", "has_case": False, "has_letters": True}
    syntax_iterators = SYNTAX_ITERATORS


class Persian(Language):
    lang = "fa"
    Defaults = PersianDefaults


__all__ = ["Persian"]
