from typing import Set, Dict, Callable, Any
from thinc.api import Config

from .stop_words import STOP_WORDS
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .lex_attrs import LEX_ATTRS
from .lemmatizer import RussianLemmatizer
from ...util import registry
from ...language import Language


DEFAULT_CONFIG = """
[nlp]
lang = "ru"
stop_words = {"@language_data": "spacy.ru.stop_words"}
lex_attr_getters = {"@language_data": "spacy.ru.lex_attr_getters"}

[nlp.lemmatizer]
@lemmatizers = "spacy.RussianLemmatizer.v1"

[nlp.vocab_data]
@language_data = "spacy-lookups-data"
lang = ${nlp:lang}
tables = ["lexeme_norm"]
"""


@registry.language_data("spacy.ru.stop_words")
def stop_words() -> Set[str]:
    return STOP_WORDS


@registry.language_data("spacy.ru.lex_attr_getters")
def lex_attr_getters() -> Dict[int, Callable[[str], Any]]:
    return LEX_ATTRS


@registry.lemmatizers("spacy.RussianLemmatizer.v1")
def create_russian_lemmatizer() -> RussianLemmatizer:
    return RussianLemmatizer()


class RussianDefaults(Language.Defaults):
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS


class Russian(Language):
    lang = "ru"
    Defaults = RussianDefaults
    default_config = Config().from_str(DEFAULT_CONFIG)


__all__ = ["Russian"]
