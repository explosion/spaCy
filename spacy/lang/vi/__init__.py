# coding: utf8
from __future__ import unicode_literals

from ...attrs import LANG
from ...language import Language
from ...tokens import Doc


class VietnameseDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters[LANG] = lambda text: 'vi'  # for pickling


class Vietnamese(Language):
    lang = 'vi'
    Defaults = VietnameseDefaults  # override defaults


__all__ = ['Vietnamese']
