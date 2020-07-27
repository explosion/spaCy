from .stop_words import STOP_WORDS
from ...language import Language


class MarathiDefaults(Language.Defaults):
    stop_words = STOP_WORDS


class Marathi(Language):
    lang = "mr"
    Defaults = MarathiDefaults


__all__ = ["Marathi"]
