from ...language import BaseDefaults, Language
from .stop_words import STOP_WORDS


class GujaratiDefaults(BaseDefaults):
    stop_words = STOP_WORDS


class Gujarati(Language):
    lang = "gu"
    Defaults = GujaratiDefaults


__all__ = ["Gujarati"]
