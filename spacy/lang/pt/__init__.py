# coding: utf8
from __future__ import unicode_literals

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from .tag_map import TAG_MAP

from ..tokenizer_exceptions import BASE_EXCEPTIONS
from .punctuation import TOKENIZER_INFIXES, TOKENIZER_PREFIXES
from ...language import Language
from ...attrs import LANG
from ...util import update_exc


class PortugueseDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters[LANG] = lambda text: "pt"
    lex_attr_getters.update(LEX_ATTRS)
    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)
    stop_words = STOP_WORDS
    tag_map = TAG_MAP
    infixes = TOKENIZER_INFIXES
    prefixes = TOKENIZER_PREFIXES


class Portuguese(Language):
    lang = "pt"
    Defaults = PortugueseDefaults


__all__ = ["Portuguese"]
