from ...language import BaseDefaults, Language
from .stop_words import STOP_WORDS


class EstonianDefaults(BaseDefaults):
    stop_words = STOP_WORDS


class Estonian(Language):
    lang = "et"
    Defaults = EstonianDefaults


__all__ = ["Estonian"]
