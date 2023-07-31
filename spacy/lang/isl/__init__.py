from ...language import BaseDefaults, Language
from .stop_words import STOP_WORDS


class IcelandicDefaults(BaseDefaults):
    stop_words = STOP_WORDS


class Icelandic(Language):
    lang = "isl"
    Defaults = IcelandicDefaults


__all__ = ["Icelandic"]
