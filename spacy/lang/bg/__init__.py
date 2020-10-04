from .stop_words import STOP_WORDS
from ...language import Language


class BulgarianDefaults(Language.Defaults):
    stop_words = STOP_WORDS


class Bulgarian(Language):
    lang = "bg"
    Defaults = BulgarianDefaults


__all__ = ["Bulgarian"]
