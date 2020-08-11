# coding: utf8
from __future__ import unicode_literals

from .stop_words import STOP_WORDS

from ...language import Language


class WelshDefaults(Language.Defaults):
    stop_words = STOP_WORDS


class Welsh(Language):
    lang = "cy"
    Defaults = WelshDefaults


__all__ = ["Welsh"]
