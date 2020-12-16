# coding: utf8
from __future__ import unicode_literals

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .punctuation import TOKENIZER_INFIXES, TOKENIZER_SUFFIXES
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from .morph_rules import MORPH_RULES
from ..tag_map import TAG_MAP

from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ...language import Language
from ...attrs import LANG
from ...util import update_exc


class DanishDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters.update(LEX_ATTRS)
    lex_attr_getters[LANG] = lambda text: "da"
    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)
    morph_rules = MORPH_RULES
    infixes = TOKENIZER_INFIXES
    suffixes = TOKENIZER_SUFFIXES
    tag_map = TAG_MAP
    stop_words = STOP_WORDS


class Danish(Language):
    lang = "da"
    Defaults = DanishDefaults


__all__ = ["Danish"]
