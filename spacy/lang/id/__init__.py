from .stop_words import STOP_WORDS
from .punctuation import TOKENIZER_SUFFIXES, TOKENIZER_PREFIXES, TOKENIZER_INFIXES
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .lex_attrs import LEX_ATTRS
from .syntax_iterators import SYNTAX_ITERATORS
from ...language import Language
from ...util import load_config_from_str


DEFAULT_CONFIG = """
[initialize]

[initialize.lookups]
@misc = "spacy.LookupsDataLoader.v1"
lang = ${nlp.lang}
tables = ["lexeme_norm"]
"""


class IndonesianDefaults(Language.Defaults):
    config = load_config_from_str(DEFAULT_CONFIG)
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    prefixes = TOKENIZER_PREFIXES
    suffixes = TOKENIZER_SUFFIXES
    infixes = TOKENIZER_INFIXES
    syntax_iterators = SYNTAX_ITERATORS
    lex_attr_getters = LEX_ATTRS
    stop_words = STOP_WORDS


class Indonesian(Language):
    lang = "id"
    Defaults = IndonesianDefaults


__all__ = ["Indonesian"]
