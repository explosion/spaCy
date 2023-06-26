from ...language import BaseDefaults, Language
from .stop_words import STOP_WORDS


class LatvianDefaults(BaseDefaults):
    stop_words = STOP_WORDS


class Latvian(Language):
    lang = "lv"
    Defaults = LatvianDefaults


__all__ = ["Latvian"]
