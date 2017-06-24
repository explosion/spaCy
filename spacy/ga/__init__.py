from .language_data import *

class Irish(Language):
    lang = 'ga' # ISO code

    class Defaults(Language.Defaults):
        lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
        lex_attr_getters[LANG] = lambda text: 'ga'

        stop_words = STOP_WORDS
        tokenizer_exceptions = TOKENIZER_EXCEPTIONS
