from ...language import BaseDefaults, Language
from .stop_words import STOP_WORDS

class KurmanjiDefaults(BaseDefaults):
    stop_words = STOP_WORDS


class Kurmanji(Language):
    lang = "kmr"
    Defaults = KurmanjiDefaults

__all__ = ["Kurmanji"]
