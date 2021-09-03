from .stop_words import STOP_WORDS
from ...language import Language


class SlovenianDefaults(Language.Defaults):  # type: ignore[misc, valid-type]
    stop_words = STOP_WORDS


class Slovenian(Language):
    lang = "sl"
    Defaults = SlovenianDefaults


__all__ = ["Slovenian"]
