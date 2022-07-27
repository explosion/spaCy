from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS

class LatinDefaults(BaseDefaults):
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS


class Latin(Language):
    lang = "la"
    Defaults = LatinDefaults


__all__ = ["Latin"]
