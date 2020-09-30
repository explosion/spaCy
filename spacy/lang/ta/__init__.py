from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from ...language import Language
from ...util import load_config_from_str


DEFAULT_CONFIG = """
[initialize]

[initialize.lookups]
@misc = "spacy.LookupsDataLoader.v1"
lang = ${nlp.lang}
tables = ["lexeme_norm"]
"""


class TamilDefaults(Language.Defaults):
    config = load_config_from_str(DEFAULT_CONFIG)
    lex_attr_getters = LEX_ATTRS
    stop_words = STOP_WORDS


class Tamil(Language):
    lang = "ta"
    Defaults = TamilDefaults


__all__ = ["Tamil"]
