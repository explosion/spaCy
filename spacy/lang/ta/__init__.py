from typing import Set, Dict, Callable, Any
from thinc.api import Config

from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from ...language import Language
from ...util import registry


DEFAULT_CONFIG = """
[nlp]
lang = "ta"
stop_words = {"@language_data": "spacy.ta.stop_words"}
lex_attr_getters = {"@language_data": "spacy.ta.lex_attr_getters"}

[nlp.vocab_data]
@language_data = "spacy-lookups-data"
lang = ${nlp:lang}
tables = ["lexeme_norm"]
"""


@registry.language_data("spacy.ta.stop_words")
def stop_words() -> Set[str]:
    return STOP_WORDS


@registry.language_data("spacy.ta.lex_attr_getters")
def lex_attr_getters() -> Dict[int, Callable[[str], Any]]:
    return LEX_ATTRS


class Tamil(Language):
    lang = "ta"
    default_config = Config().from_str(DEFAULT_CONFIG)


__all__ = ["Tamil"]
