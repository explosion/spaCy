from .stop_words import STOP_WORDS
from ...language import Language


class LatvianDefaults(Language.Defaults):  # type: ignore[misc, valid-type]
    stop_words = STOP_WORDS


class Latvian(Language):
    lang = "lv"
    Defaults = LatvianDefaults


__all__ = ["Latvian"]
