from .stop_words import STOP_WORDS
from ...language import Language


class CzechDefaults(Language.Defaults):
    stop_words = STOP_WORDS


class Czech(Language):
    lang = "cs"
    Defaults = CzechDefaults


__all__ = ["Czech"]
