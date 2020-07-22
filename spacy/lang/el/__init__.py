from typing import Set, Dict, Callable, Any
from thinc.api import Config

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from .lemmatizer import GreekLemmatizer
from .syntax_iterators import noun_chunks
from .punctuation import TOKENIZER_PREFIXES, TOKENIZER_SUFFIXES, TOKENIZER_INFIXES
from ...language import Language
from ...util import registry


DEFAULT_CONFIG = """
[nlp]
lang = "el"
stop_words = {"@language_data": "spacy.el.stop_words"}
lex_attr_getters = {"@language_data": "spacy.el.lex_attr_getters"}
get_noun_chunks = {"@language_data": "spacy.el.get_noun_chunks"}

[nlp.lemmatizer]
@lemmatizers = "spacy.GreekLemmatizer.v1"

[nlp.lemmatizer.data]
@language_data = "spacy-lookups-data"
lang = ${nlp:lang}
tables = ["lemma_index", "lemma_exc", "lemma_rules"]

[nlp.vocab_data]
@language_data = "spacy-lookups-data"
lang = ${nlp:lang}
tables = ["lexeme_norm", "lexeme_prob", "lexeme_settings"]
"""


@registry.lemmatizers("spacy.GreekLemmatizer.v1")
def create_greek_lemmatizer(data: Dict[str, dict] = {}) -> GreekLemmatizer:
    return GreekLemmatizer(data=data)


@registry.language_data("spacy.el.get_noun_chunks")
def get_noun_chunks() -> Callable:
    return noun_chunks


@registry.language_data("spacy.el.stop_words")
def stop_words() -> Set[str]:
    return STOP_WORDS


@registry.language_data("spacy.el.lex_attr_getters")
def lex_attr_getters() -> Dict[int, Callable[[str], Any]]:
    return LEX_ATTRS


class GreekDefaults(Language.Defaults):
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    prefixes = TOKENIZER_PREFIXES
    suffixes = TOKENIZER_SUFFIXES
    infixes = TOKENIZER_INFIXES


class Greek(Language):
    lang = "el"
    Defaults = GreekDefaults
    default_config = Config().from_str(DEFAULT_CONFIG)


__all__ = ["Greek"]
