# encoding: utf8
from __future__ import unicode_literals, print_function

from os import path

from ..language import Language
from . import language_data
from ..attrs import LANG

from ..language_data import update_exc
from ..language_data import EMOTICONS
from .language_data import ORTH_ONLY
from .language_data import strings_to_exc


TOKENIZER_EXCEPTIONS = dict(language_data.TOKENIZER_EXCEPTIONS)
TOKENIZER_PREFIXES = tuple(language_data.TOKENIZER_PREFIXES)
TOKENIZER_SUFFIXES = tuple(language_data.TOKENIZER_SUFFIXES)
TOKENIZER_INFIXES = tuple(language_data.TOKENIZER_INFIXES)
TAG_MAP = dict(language_data.TAG_MAP)
STOP_WORDS = set(language_data.STOP_WORDS)


update_exc(TOKENIZER_EXCEPTIONS, strings_to_exc(EMOTICONS))
update_exc(TOKENIZER_EXCEPTIONS, strings_to_exc(ORTH_ONLY))


class Spanish(Language):
    lang = 'es'

    class Defaults(Language.Defaults):
        lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
        lex_attr_getters[LANG] = lambda text: 'es'

        tokenizer_exceptions = TOKENIZER_EXCEPTIONS
        prefixes = TOKENIZER_PREFIXES
        suffixes = TOKENIZER_SUFFIXES
        infixes = TOKENIZER_INFIXES
        tag_map = TAG_MAP
        stop_words = STOP_WORDS
