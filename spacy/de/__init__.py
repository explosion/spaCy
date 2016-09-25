from __future__ import unicode_literals, print_function

from os import path

from ..language import Language
from . import language_data


class German(Language):
    lang = 'de'
    
    class Defaults(Language.Defaults):
        tokenizer_exceptions = dict(language_data.TOKENIZER_EXCEPTIONS)
        
        prefixes = tuple(language_data.TOKENIZER_PREFIXES)
        
        suffixes = tuple(language_data.TOKENIZER_SUFFIXES)
        
        infixes = tuple(language_data.TOKENIZER_INFIXES)

        tag_map = dict(language_data.TAG_MAP)

        stop_words = set(language_data.STOP_WORDS)

