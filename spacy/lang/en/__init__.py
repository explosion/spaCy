from typing import Set, Dict, Callable, Any
from thinc.api import Config

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from .syntax_iterators import noun_chunks
from .lemmatizer import is_base_form
from .punctuation import TOKENIZER_INFIXES
from ...language import Language
from ...lemmatizer import Lemmatizer
from ...util import registry


DEFAULT_CONFIG = """
[nlp]
lang = "en"
stop_words = {"@language_data": "spacy.en.stop_words"}
lex_attr_getters = {"@language_data": "spacy.en.lex_attr_getters"}
get_noun_chunks = {"@language_data": "spacy.en.get_noun_chunks"}

[nlp.lemmatizer]
@lemmatizers = "spacy.EnglishLemmatizer.v1"

[nlp.lemmatizer.data]
@language_data = "spacy-lookups-data"
lang = ${nlp:lang}
tables = ["lemma_lookup", "lemma_rules", "lemma_exc", "lemma_index"]

[nlp.vocab_data]
@language_data = "spacy-lookups-data"
lang = ${nlp:lang}
tables = ["lexeme_norm", "lexeme_cluster", "lexeme_prob", "lexeme_settings", "orth_variants"]
"""


@registry.language_data("spacy.en.stop_words")
def stop_words() -> Set[str]:
    return STOP_WORDS


@registry.language_data("spacy.en.lex_attr_getters")
def lex_attr_getters() -> Dict[int, Callable[[str], Any]]:
    return LEX_ATTRS


@registry.lemmatizers("spacy.EnglishLemmatizer.v1")
def create_lemmatizer(data: Dict[str, dict] = {}) -> "Lemmatizer":
    return Lemmatizer(data=data, is_base_form=is_base_form)


@registry.language_data("spacy.en.get_noun_chunks")
def get_noun_chunks() -> Callable:
    return noun_chunks


class EnglishDefaults(Language.Defaults):
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    infixes = TOKENIZER_INFIXES


class English(Language):
    lang = "en"
    Defaults = EnglishDefaults
    default_config = Config().from_str(DEFAULT_CONFIG)


__all__ = ["English"]
