from .stop_words import STOP_WORDS
from ...language import Language


class LatvianDefaults(Language.Defaults):
    stop_words = STOP_WORDS


class Latvian(Language):
    lang = "lv"
    Defaults = LatvianDefaults


__all__ = ["Latvian"]
