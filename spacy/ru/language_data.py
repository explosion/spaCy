# encoding: utf8

#
#   Developed by Expasoft Ltd.
#   Website: https://expasoft.ru/
#
#   Developer: Alexey Kim
#   GitHub: @yuukos
#

from __future__ import unicode_literals

from .. import language_data as base
from ..language_data import update_exc, strings_to_exc

from .stop_words import STOP_WORDS
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS


STOP_WORDS = set(STOP_WORDS)
TOKENIZER_EXCEPTIONS = dict(TOKENIZER_EXCEPTIONS)


update_exc(TOKENIZER_EXCEPTIONS, strings_to_exc(base.EMOTICONS))


__all__ = ["STOP_WORDS", "TOKENIZER_EXCEPTIONS"]
