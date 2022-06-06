'''

__init__.py:This defines the defaults and Language subclass
Further we need the following
Punctuation: Punctuation chars(?) for Luganda
Stopwords: Frequent words that appear often in Luganda
Syntax iterators: Functions that compute views of a Doc object based on its syntax, e.g. Noun chunks
Tokenizer exception: Special-case rules for the tokenizer, for example, contractions like “ebye'mizannyo” and abbreviations with punctuation, like “Owek.”.

'''

from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from ...language import Language, BaseDefaults


class LugandaDefaults(BaseDefaults):
    lex_attr_getters = LEX_ATTRS
    stop_words = STOP_WORDS


class Luganda(Language):
    lang = "lg"
    Defaults = LugandaDefaults


__all__ = ["Luganda"]
