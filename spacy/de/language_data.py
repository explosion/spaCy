# encoding: utf8
from __future__ import unicode_literals

from .. import language_data as base
from ..language_data import update_exc, strings_to_exc

from .tag_map import TAG_MAP
from .stop_words import STOP_WORDS
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS, ORTH_ONLY


TOKENIZER_EXCEPTIONS = dict(TOKENIZER_EXCEPTIONS)
TAG_MAP = dict(TAG_MAP)
STOP_WORDS = set(STOP_WORDS)


update_exc(TOKENIZER_EXCEPTIONS, strings_to_exc(ORTH_ONLY))
update_exc(TOKENIZER_EXCEPTIONS, strings_to_exc(base.EMOTICONS))


__all__ = ["TOKENIZER_EXCEPTIONS", "TAG_MAP", "STOP_WORDS"]
