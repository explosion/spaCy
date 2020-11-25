from .stop_words import STOP_WORDS
from .tag_map import TAG_MAP

from ...language import Language


class CroatianDefaults(Language.Defaults):
    stop_words = STOP_WORDS
    tag_map = TAG_MAP


class Croatian(Language):
    lang = "hr"
    Defaults = CroatianDefaults


__all__ = ["Croatian"]
