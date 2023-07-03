from ...language import BaseDefaults, Language
from .stop_words import STOP_WORDS


class AlbanianDefaults(BaseDefaults):
    stop_words = STOP_WORDS


class Albanian(Language):
    lang = "sq"
    Defaults = AlbanianDefaults


__all__ = ["Albanian"]
