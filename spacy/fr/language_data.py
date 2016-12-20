# encoding: utf8
from __future__ import unicode_literals

from .. import language_data as base
from ..language_data import strings_to_exc

from .stop_words import STOP_WORDS


TOKENIZER_EXCEPTIONS = strings_to_exc(base.EMOTICONS)
STOP_WORDS = set(STOP_WORDS)


__all__ = ["TOKENIZER_EXCEPTIONS", "STOP_WORDS"]
