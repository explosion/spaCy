from __future__ import unicode_literals, print_function

from os import path

from ..language import Language
from . import language_data
from .. import util
from ..lemmatizer import Lemmatizer
from ..vocab import Vocab
from ..tokenizer import Tokenizer
from ..attrs import LANG


class English(Language):
    lang = 'en'

    class Defaults(Language.Defaults):
        lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
        lex_attr_getters[LANG] = lambda text: 'en'

        tokenizer_exceptions = dict(language_data.TOKENIZER_EXCEPTIONS)
 
        prefixes = tuple(language_data.TOKENIZER_PREFIXES)

        suffixes = tuple(language_data.TOKENIZER_SUFFIXES)

        infixes = tuple(language_data.TOKENIZER_INFIXES)

        tag_map = dict(language_data.TAG_MAP)

        stop_words = set(language_data.STOP_WORDS)
