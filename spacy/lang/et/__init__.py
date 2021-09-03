from .stop_words import STOP_WORDS
from ...language import Language


class EstonianDefaults(Language.Defaults):  # type: ignore[misc, valid-type]
    stop_words = STOP_WORDS


class Estonian(Language):
    lang = "et"
    Defaults = EstonianDefaults


__all__ = ["Estonian"]
