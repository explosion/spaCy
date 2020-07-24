from typing import Callable
from thinc.api import Config

from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .punctuation import TOKENIZER_PREFIXES, TOKENIZER_INFIXES
from .punctuation import TOKENIZER_SUFFIXES
from .lemmatizer import DutchLemmatizer
from ...lookups import load_lookups
from ...language import Language
from ...util import registry


DEFAULT_CONFIG = """
[nlp]

[nlp.lemmatizer]
@lemmatizers = "spacy.nl.DutchLemmatizer"
"""


@registry.lemmatizers("spacy.nl.DutchLemmatizer")
def create_lemmatizer() -> Callable[[Language], DutchLemmatizer]:
    tables = ["lemma_rules", "lemma_index", "lemma_exc", "lemma_lookup"]

    def lemmatizer_factory(nlp: Language) -> DutchLemmatizer:
        lookups = load_lookups(lang=nlp.lang, tables=tables)
        return DutchLemmatizer(lookups=lookups)

    return lemmatizer_factory


class DutchDefaults(Language.Defaults):
    config = Config().from_str(DEFAULT_CONFIG)
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    prefixes = TOKENIZER_PREFIXES
    infixes = TOKENIZER_INFIXES
    suffixes = TOKENIZER_SUFFIXES
    lex_attr_getters = LEX_ATTRS
    stop_words = STOP_WORDS


class Dutch(Language):
    lang = "nl"
    Defaults = DutchDefaults


__all__ = ["Dutch"]
