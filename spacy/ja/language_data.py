# encoding: utf8
from __future__ import unicode_literals


# import base language data
from .. import language_data as base


# import util functions
from ..language_data import update_exc, strings_to_exc


# import language-specific data from files
from .tag_map import TAG_MAP
from .stop_words import STOP_WORDS


TAG_MAP = dict(TAG_MAP)
STOP_WORDS = set(STOP_WORDS)


# export
__all__ = ["TAG_MAP", "STOP_WORDS"]
