from .stop_words import STOP_WORDS
from ...language import Language


class IcelandicDefaults(Language.Defaults):
    stop_words = STOP_WORDS


class Icelandic(Language):
    lang = "is"
    Defaults = IcelandicDefaults


__all__ = ["Icelandic"]
