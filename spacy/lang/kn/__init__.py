from ...language import BaseDefaults, Language
from .stop_words import STOP_WORDS


class KannadaDefaults(BaseDefaults):
    stop_words = STOP_WORDS


class Kannada(Language):
    lang = "kn"
    Defaults = KannadaDefaults


__all__ = ["Kannada"]
