from typing import Set, Dict, Callable, Any
from thinc.api import Config

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from ...language import Language
from ...util import registry
from .punctuation import TOKENIZER_INFIXES


DEFAULT_CONFIG = """
[nlp]
lang = "ca"
stop_words = {"@language_data": "spacy.ca.stop_words"}
lex_attr_getters = {"@language_data": "spacy.ca.lex_attr_getters"}

[nlp.lemmatizer]
@lemmatizers = "spacy.Lemmatizer.v1"

[nlp.lemmatizer.data]
@language_data = "spacy-lookups-data"
lang = ${nlp:lang}
tables = ["lemma_lookup"]
"""


@registry.language_data("spacy.ca.stop_words")
def stop_words() -> Set[str]:
    return STOP_WORDS


@registry.language_data("spacy.ca.lex_attr_getters")
def lex_attr_getters() -> Dict[int, Callable[[str], Any]]:
    return LEX_ATTRS


class CatalanDefaults(Language.Defaults):
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    infixes = TOKENIZER_INFIXES


class Catalan(Language):
    lang = "ca"
    Defaults = CatalanDefaults
    default_config = Config().from_str(DEFAULT_CONFIG)


__all__ = ["Catalan"]
