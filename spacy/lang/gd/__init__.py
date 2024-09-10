from typing import Optional

from ...language import BaseDefaults, Language
from .stop_words import STOP_WORDS
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS


class ScottishDefaults(BaseDefaults):
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    stop_words = STOP_WORDS


class Scottish(Language):
    lang = "gd"
    Defaults = ScottishDefaults


__all__ = ["Scottish"]
