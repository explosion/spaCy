from typing import Set, Dict, Callable, Any
from thinc.api import Config

from .punctuation import TOKENIZER_INFIXES, TOKENIZER_SUFFIXES
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ...language import Language
from ...util import update_exc, registry


DEFAULT_CONFIG = """
[nlp]
lang = "lt"
stop_words = {"@language_data": "spacy.lt.stop_words"}
lex_attr_getters = {"@language_data": "spacy.lt.lex_attr_getters"}

[nlp.lemmatizer]
@lemmatizers = "spacy.Lemmatizer.v1"

[nlp.lemmatizer.data_paths]
@language_data = "spacy-lookups-data"
lang = ${nlp:lang}
"""


@registry.language_data("spacy.lt.stop_words")
def stop_words() -> Set[str]:
    return STOP_WORDS


@registry.language_data("spacy.lt.lex_attr_getters")
def lex_attr_getters() -> Dict[int, Callable[[str], Any]]:
    return LEX_ATTRS


class LithuanianDefaults(Language.Defaults):
    infixes = TOKENIZER_INFIXES
    suffixes = TOKENIZER_SUFFIXES
    mod_base_exceptions = {
        exc: val for exc, val in BASE_EXCEPTIONS.items() if not exc.endswith(".")
    }
    del mod_base_exceptions["8)"]
    tokenizer_exceptions = update_exc(mod_base_exceptions, TOKENIZER_EXCEPTIONS)


class Lithuanian(Language):
    lang = "lt"
    Defaults = LithuanianDefaults
    default_config = Config().from_str(DEFAULT_CONFIG)


__all__ = ["Lithuanian"]
