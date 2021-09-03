from .stop_words import STOP_WORDS
from ...language import Language


class CroatianDefaults(Language.Defaults):  # type: ignore[misc, valid-type]
    stop_words = STOP_WORDS


class Croatian(Language):
    lang = "hr"
    Defaults = CroatianDefaults


__all__ = ["Croatian"]
