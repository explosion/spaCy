# coding: utf8
from __future__ import unicode_literals

from .stop_words import STOP_WORDS

from ...language import Language


class GujaratiDefaults(Language.Defaults):
    stop_words = STOP_WORDS


class Gujarati(Language):
    lang = "gu"
    Defaults = GujaratiDefaults


__all__ = ["Gujarati"]
