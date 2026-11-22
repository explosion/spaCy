from ...language import BaseDefaults, Language
from ..tokenizer_exceptions import BASE_EXCEPTIONS
from .lex_attrs import LEX_ATTRS
from .punctuation import TOKENIZER_INFIXES, TOKENIZER_SUFFIXES
from .stop_words import STOP_WORDS

# Abbreviations are split from their period, as in the Czech UD treebanks
# ("např." -> "např", "."), so the base exceptions ending in a period are
# dropped (same approach as Polish).
TOKENIZER_EXCEPTIONS = {
    exc: val for exc, val in BASE_EXCEPTIONS.items() if not exc.endswith(".")
}


class CzechDefaults(BaseDefaults):
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    infixes = TOKENIZER_INFIXES
    suffixes = TOKENIZER_SUFFIXES
    lex_attr_getters = LEX_ATTRS
    stop_words = STOP_WORDS


class Czech(Language):
    lang = "cs"
    Defaults = CzechDefaults


__all__ = ["Czech"]
