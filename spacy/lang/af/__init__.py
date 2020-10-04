from .stop_words import STOP_WORDS
from ...language import Language


class AfrikaansDefaults(Language.Defaults):
    stop_words = STOP_WORDS


class Afrikaans(Language):
    lang = "af"
    Defaults = AfrikaansDefaults


__all__ = ["Afrikaans"]
