from typing import Set, Dict, Callable, Any, Pattern
from thinc.api import Config

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS, TOKEN_MATCH
from .punctuation import TOKENIZER_PREFIXES, TOKENIZER_INFIXES
from .punctuation import TOKENIZER_SUFFIXES
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from .lemmatizer import FrenchLemmatizer, is_base_form
from .syntax_iterators import noun_chunks
from ...language import Language
from ...util import registry


DEFAULT_CONFIG = """
[nlp]
lang = "fr"
stop_words = {"@language_data": "spacy.fr.stop_words"}
lex_attr_getters = {"@language_data": "spacy.fr.lex_attr_getters"}
get_noun_chunks = {"@language_data": "spacy.fr.get_noun_chunks"}

[nlp.tokenizer]
@tokenizers = "spacy.Tokenizer.v1"
token_match = {"@language_data": "spacy.fr.token_match"}

[nlp.lemmatizer]
@lemmatizers = "spacy.FrenchLemmatizer.v1"

[nlp.lemmatizer.data]
@language_data = "spacy-lookups-data"
lang = ${nlp:lang}
tables = ["lemma_rules", "lemma_index", "lemma_exc", "lemma_lookup"]
"""


@registry.lemmatizers("spacy.FrenchLemmatizer.v1")
def create_french_lemmatizer(data: Dict[str, dict] = {}) -> FrenchLemmatizer:
    return FrenchLemmatizer(data=data, is_base_form=is_base_form)


@registry.language_data("spacy.fr.token_match")
def token_match() -> Pattern:
    return TOKEN_MATCH


@registry.language_data("spacy.fr.stop_words")
def stop_words() -> Set[str]:
    return STOP_WORDS


@registry.language_data("spacy.fr.lex_attr_getters")
def lex_attr_getters() -> Dict[int, Callable[[str], Any]]:
    return LEX_ATTRS


@registry.language_data("spacy.fr.get_noun_chunks")
def get_noun_chunks() -> Callable:
    return noun_chunks


class FrenchDefaults(Language.Defaults):
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    prefixes = TOKENIZER_PREFIXES
    infixes = TOKENIZER_INFIXES
    suffixes = TOKENIZER_SUFFIXES


class French(Language):
    lang = "fr"
    Defaults = FrenchDefaults
    default_config = Config().from_str(DEFAULT_CONFIG)


__all__ = ["French"]
