from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from .punctuation import TOKENIZER_INFIXES, TOKENIZER_PREFIXES
from ...language import Language
from ...util import load_config_from_str


DEFAULT_CONFIG = """
[initialize]

[initialize.lookups]
@misc = "spacy.LookupsDataLoader.v1"
lang = ${nlp.lang}
tables = ["lexeme_norm"]
"""


class PortugueseDefaults(Language.Defaults):
    config = load_config_from_str(DEFAULT_CONFIG)
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    infixes = TOKENIZER_INFIXES
    prefixes = TOKENIZER_PREFIXES
    lex_attr_getters = LEX_ATTRS
    stop_words = STOP_WORDS


class Portuguese(Language):
    lang = "pt"
    Defaults = PortugueseDefaults


__all__ = ["Portuguese"]
