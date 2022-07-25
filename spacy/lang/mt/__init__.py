from .stop_words import STOP_WORDS
from ...language import Language, BaseDefaults


class MalteseDefaults(BaseDefaults):
    stop_words = STOP_WORDS


class Maltese(Language):
    lang = "mt"
    Defaults = MalteseDefaults


__all__ = ["Maltese"]
