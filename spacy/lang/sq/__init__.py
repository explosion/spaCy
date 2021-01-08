from .stop_words import STOP_WORDS
from ...language import Language


class AlbanianDefaults(Language.Defaults):
    stop_words = STOP_WORDS


class Albanian(Language):
    lang = "sq"
    Defaults = AlbanianDefaults


__all__ = ["Albanian"]
