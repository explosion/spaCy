from ...language import BaseDefaults, Language
from .stop_words import STOP_WORDS


class CroatianDefaults(BaseDefaults):
    stop_words = STOP_WORDS


class Croatian(Language):
    lang = "hr"
    Defaults = CroatianDefaults


__all__ = ["Croatian"]
