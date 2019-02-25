# coding: utf8
from __future__ import unicode_literals

from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS

from ..norm_exceptions import BASE_NORMS
from ...language import Language
from ...attrs import LANG


class KannadaDefaults(Language.Defaults):
    stop_words = STOP_WORDS


class Kannada(Language):
    lang = 'kn'
    Defaults = KannadaDefaults


__all__ = ['Kannada']
