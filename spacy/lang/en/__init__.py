from typing import Set, Dict, Callable, Any
from thinc.api import Config

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from .syntax_iterators import SYNTAX_ITERATORS
from .lemmatizer import is_base_form
from .punctuation import TOKENIZER_INFIXES
from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ...language import Language
from ...lemmatizer import Lemmatizer
from ...util import update_exc, registry


DEFAULT_CONFIG = """
[nlp]
lang = "en"
stop_words = {"@language_data": "spacy.en.stop_words"}
lex_attr_getters = {"@language_data": "spacy.en.lex_attr_getters"}

[nlp.lemmatizer]
@lemmatizers = "spacy.EnglishLemmatizer.v1"

[nlp.lemmatizer.data_paths]
@language_data = "spacy-lookups-data"
lang = ${nlp:lang}
"""


@registry.language_data("spacy.en.stop_words")
def stop_words() -> Set[str]:
    return STOP_WORDS


@registry.language_data("spacy.en.lex_attr_getters")
def lex_attr_getters() -> Dict[int, Callable[[str], Any]]:
    return LEX_ATTRS


@registry.lemmatizers("spacy.EnglishLemmatizer.v1")
def create_lemmatizer(data_paths: dict = {}) -> "Lemmatizer":
    return Lemmatizer(data_paths=data_paths, is_base_form=is_base_form)


class EnglishDefaults(Language.Defaults):
    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)
    syntax_iterators = SYNTAX_ITERATORS
    infixes = TOKENIZER_INFIXES
    single_orth_variants = [
        {"tags": ["NFP"], "variants": ["…", "..."]},
        {"tags": [":"], "variants": ["-", "—", "–", "--", "---", "——"]},
    ]
    paired_orth_variants = [
        {"tags": ["``", "''"], "variants": [("'", "'"), ("‘", "’")]},
        {"tags": ["``", "''"], "variants": [('"', '"'), ("“", "”")]},
    ]


class English(Language):
    lang = "en"
    Defaults = EnglishDefaults
    default_config = Config().from_str(DEFAULT_CONFIG)


__all__ = ["English"]
