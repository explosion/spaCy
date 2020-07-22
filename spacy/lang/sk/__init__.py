from typing import Set, Dict, Callable, Any
from thinc.api import Config

from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from ...language import Language
from ...util import registry


DEFAULT_CONFIG = """
[nlp]
lang = "sk"
stop_words = {"@language_data": "spacy.sk.stop_words"}
lex_attr_getters = {"@language_data": "spacy.sk.lex_attr_getters"}
"""


@registry.language_data("spacy.sk.stop_words")
def stop_words() -> Set[str]:
    return STOP_WORDS


@registry.language_data("spacy.sk.lex_attr_getters")
def lex_attr_getters() -> Dict[int, Callable[[str], Any]]:
    return LEX_ATTRS


class Slovak(Language):
    lang = "sk"
    default_config = Config().from_str(DEFAULT_CONFIG)


__all__ = ["Slovak"]
