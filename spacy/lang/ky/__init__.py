# coding: utf8
from __future__ import unicode_literals

from .lex_attrs import LEX_ATTRS
from .punctuation import TOKENIZER_INFIXES
from .stop_words import STOP_WORDS
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ...attrs import LANG
from ...language import Language
from ...util import update_exc


class KyrgyzDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters[LANG] = lambda text: "ky"

    lex_attr_getters.update(LEX_ATTRS)

    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)
    infixes = tuple(TOKENIZER_INFIXES)

    stop_words = STOP_WORDS


class Kyrgyz(Language):
    lang = "ky"
    Defaults = KyrgyzDefaults


__all__ = ["Kyrgyz"]
