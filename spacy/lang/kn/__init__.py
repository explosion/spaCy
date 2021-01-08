from .stop_words import STOP_WORDS
from ...language import Language


class KannadaDefaults(Language.Defaults):
    stop_words = STOP_WORDS


class Kannada(Language):
    lang = "kn"
    Defaults = KannadaDefaults


__all__ = ["Kannada"]
