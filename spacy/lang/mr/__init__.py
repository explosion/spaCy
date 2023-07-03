from ...language import BaseDefaults, Language
from .stop_words import STOP_WORDS


class MarathiDefaults(BaseDefaults):
    stop_words = STOP_WORDS


class Marathi(Language):
    lang = "mr"
    Defaults = MarathiDefaults


__all__ = ["Marathi"]
