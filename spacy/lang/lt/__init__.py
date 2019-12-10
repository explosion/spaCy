# coding: utf8
from __future__ import unicode_literals

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from .tag_map import TAG_MAP
from .morph_rules import MORPH_RULES

from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ..norm_exceptions import BASE_NORMS
from ...language import Language
from ...attrs import LANG, NORM
from ...util import update_exc, add_lookups


def _return_lt(_):
    return "lt"


class LithuanianDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters[LANG] = _return_lt
    lex_attr_getters[NORM] = add_lookups(
        Language.Defaults.lex_attr_getters[NORM], BASE_NORMS
    )
    lex_attr_getters.update(LEX_ATTRS)

    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)
    stop_words = STOP_WORDS
    tag_map = TAG_MAP
    morph_rules = MORPH_RULES


class Lithuanian(Language):
    lang = "lt"
    Defaults = LithuanianDefaults


__all__ = ["Lithuanian"]
