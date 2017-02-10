# encoding: utf8
from __future__ import unicode_literals

from .stop_words import STOP_WORDS
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS, TOKEN_MATCH


STOP_WORDS = set(STOP_WORDS)


__all__ = ["STOP_WORDS", "TOKENIZER_EXCEPTIONS", "TOKEN_MATCH"]
