# coding: utf8
from __future__ import unicode_literals

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS, TOKEN_MATCH
from .stop_words import STOP_WORDS
from .syntax_iterators import SYNTAX_ITERATORS
from .lex_attrs import LEX_ATTRS
from .morph_rules import MORPH_RULES


from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ..norm_exceptions import BASE_NORMS
from ...language import Language
from ...attrs import LANG, NORM
from ...util import update_exc, add_lookups


class TurkishDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters.update(LEX_ATTRS)
    lex_attr_getters[LANG] = lambda text: "tr"
    lex_attr_getters[NORM] = add_lookups(
        Language.Defaults.lex_attr_getters[NORM], BASE_NORMS
    )
    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)
    stop_words = STOP_WORDS
    token_match = TOKEN_MATCH
    syntax_iterators = SYNTAX_ITERATORS
    morph_rules = MORPH_RULES


class Turkish(Language):
    lang = "tr"
    Defaults = TurkishDefaults


__all__ = ["Turkish"]
