from __future__ import unicode_literals, print_function

from . import language_data
from ..attrs import LANG
from ..language import Language


class Hungarian(Language):
    lang = 'hu'

    class Defaults(Language.Defaults):
        tokenizer_exceptions = dict(language_data.TOKENIZER_EXCEPTIONS)
        lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
        lex_attr_getters[LANG] = lambda text: 'hu'

        prefixes = tuple(language_data.TOKENIZER_PREFIXES)

        suffixes = tuple(language_data.TOKENIZER_SUFFIXES)

        infixes = tuple(language_data.TOKENIZER_INFIXES)

        tag_map = dict(language_data.TAG_MAP)

        stop_words = set(language_data.STOP_WORDS)
