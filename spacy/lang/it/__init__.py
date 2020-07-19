from thinc.api import Config

from .stop_words import STOP_WORDS
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .punctuation import TOKENIZER_PREFIXES, TOKENIZER_INFIXES

from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ..norm_exceptions import BASE_NORMS
from ...language import Language
from ...attrs import LANG, NORM
from ...util import update_exc, add_lookups


DEFAULT_CONFIG = """
[nlp]
lang = "it"

[nlp.lemmatizer]
@lemmatizers = "spacy.Lemmatizer.v1"
data_paths = {"@lookups": "spacy-lookups-data.it"}
"""


class ItalianDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters[LANG] = lambda text: "it"
    lex_attr_getters[NORM] = add_lookups(
        Language.Defaults.lex_attr_getters[NORM], BASE_NORMS
    )
    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)
    stop_words = STOP_WORDS
    prefixes = TOKENIZER_PREFIXES
    infixes = TOKENIZER_INFIXES


class Italian(Language):
    lang = "it"
    Defaults = ItalianDefaults
    default_config = Config().from_str(DEFAULT_CONFIG)


__all__ = ["Italian"]
