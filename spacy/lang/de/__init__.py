from typing import Set
from thinc.api import Config

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .punctuation import TOKENIZER_PREFIXES, TOKENIZER_SUFFIXES
from .punctuation import TOKENIZER_INFIXES
from .stop_words import STOP_WORDS
from .syntax_iterators import SYNTAX_ITERATORS
from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ...language import Language
from ...util import update_exc, registry


DEFAULT_CONFIG = """
[nlp]
lang = "de"
stop_words = {"@language_data": "spacy.de.stop_words"}

[nlp.lemmatizer]
@lemmatizers = "spacy.Lemmatizer.v1"

[nlp.lemmatizer.data]
@language_data = "spacy-lookups-data"
lang = ${nlp:lang}
tables = ["lemma_lookup"]

[nlp.vocab_data]
@language_data = "spacy-lookups-data"
lang = ${nlp:lang}
tables = ["lexeme_norm", "lexeme_cluster", "lexeme_prob", "lexeme_settings", "orth_variants"]
"""


@registry.language_data("spacy.de.stop_words")
def stop_words() -> Set[str]:
    return STOP_WORDS


class GermanDefaults(Language.Defaults):
    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)
    prefixes = TOKENIZER_PREFIXES
    suffixes = TOKENIZER_SUFFIXES
    infixes = TOKENIZER_INFIXES
    syntax_iterators = SYNTAX_ITERATORS


class German(Language):
    lang = "de"
    Defaults = GermanDefaults
    default_config = Config().from_str(DEFAULT_CONFIG)


__all__ = ["German"]
