from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .stop_words import STOP_WORDS

class LatinDefaults(BaseDefaults):
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    stop_words = STOP_WORDS    


class Latin(Language):
    lang = "la"
    Defaults = LatinDefaults


__all__ = ["Latin"]
