from typing import Set, Dict, Callable, Any
from thinc.api import Config

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS, TOKEN_MATCH
from .punctuation import TOKENIZER_PREFIXES, TOKENIZER_INFIXES
from .punctuation import TOKENIZER_SUFFIXES
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from .lemmatizer import FrenchLemmatizer, is_base_form
from .syntax_iterators import SYNTAX_ITERATORS
from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ...language import Language
from ...util import update_exc, registry


DEFAULT_CONFIG = """
[nlp]
lang = "fr"
stop_words = {"@language_data": "spacy.fr.stop_words"}
lex_attr_getters = {"@language_data": "spacy.fr.lex_attr_getters"}

[nlp.lemmatizer]
@lemmatizers = "spacy.FrenchLemmatizer.v1"

[nlp.lemmatizer.data_paths]
@language_data = "spacy-lookups-data"
lang = ${nlp:lang}
"""


@registry.lemmatizers("spacy.FrenchLemmatizer.v1")
def create_french_lemmatizer(data_paths: dict = {}) -> FrenchLemmatizer:
    return FrenchLemmatizer(data_paths=data_paths, is_base_form=is_base_form)


@registry.language_data("spacy.fr.stop_words")
def stop_words() -> Set[str]:
    return STOP_WORDS


@registry.language_data("spacy.fr.lex_attr_getters")
def lex_attr_getters() -> Dict[int, Callable[[str], Any]]:
    return LEX_ATTRS


class FrenchDefaults(Language.Defaults):
    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)
    prefixes = TOKENIZER_PREFIXES
    infixes = TOKENIZER_INFIXES
    suffixes = TOKENIZER_SUFFIXES
    token_match = TOKEN_MATCH
    syntax_iterators = SYNTAX_ITERATORS


class French(Language):
    lang = "fr"
    Defaults = FrenchDefaults
    default_config = Config().from_str(DEFAULT_CONFIG)


__all__ = ["French"]
