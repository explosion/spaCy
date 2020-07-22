from typing import Set, Dict, Callable, Any
from thinc.api import Config

from .stop_words import STOP_WORDS
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .lex_attrs import LEX_ATTRS
from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ...language import Language
from ...util import update_exc, registry


DEFAULT_CONFIG = """
[nlp]
lang = "sr"
stop_words = {"@language_data": "spacy.sr.stop_words"}
lex_attr_getters = {"@language_data": "spacy.sr.lex_attr_getters"}

[nlp.lemmatizer]
@lemmatizers = "spacy.Lemmatizer.v1"

[nlp.lemmatizer.data]
@language_data = "spacy-lookups-data"
lang = ${nlp:lang}
tables = ["lemma_lookup"]

[nlp.vocab_data]
@language_data = "spacy-lookups-data"
lang = ${nlp:lang}
tables = ["lexeme_norm"]
"""


@registry.language_data("spacy.sr.stop_words")
def stop_words() -> Set[str]:
    return STOP_WORDS


@registry.language_data("spacy.sr.lex_attr_getters")
def lex_attr_getters() -> Dict[int, Callable[[str], Any]]:
    return LEX_ATTRS


class SerbianDefaults(Language.Defaults):
    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)


class Serbian(Language):
    lang = "sr"
    Defaults = SerbianDefaults
    default_config = Config().from_str(DEFAULT_CONFIG)


__all__ = ["Serbian"]
