from typing import Set, Dict, Callable, Any
from thinc.api import Config

from .lex_attrs import LEX_ATTRS
from .punctuation import TOKENIZER_INFIXES
from .stop_words import STOP_WORDS
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from ...language import Language
from ...util import registry


DEFAULT_CONFIG = """
[nlp]
lang = "tt"
stop_words = {"@language_data": "spacy.tt.stop_words"}
lex_attr_getters = {"@language_data": "spacy.tt.lex_attr_getters"}
"""


@registry.language_data("spacy.tt.stop_words")
def stop_words() -> Set[str]:
    return STOP_WORDS


@registry.language_data("spacy.tt.lex_attr_getters")
def lex_attr_getters() -> Dict[int, Callable[[str], Any]]:
    return LEX_ATTRS


class TatarDefaults(Language.Defaults):
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    infixes = tuple(TOKENIZER_INFIXES)


class Tatar(Language):
    lang = "tt"
    Defaults = TatarDefaults
    default_config = Config().from_str(DEFAULT_CONFIG)


__all__ = ["Tatar"]
