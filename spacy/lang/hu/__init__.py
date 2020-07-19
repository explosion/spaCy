from thinc.api import Config

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS, TOKEN_MATCH
from .punctuation import TOKENIZER_PREFIXES, TOKENIZER_SUFFIXES, TOKENIZER_INFIXES
from .stop_words import STOP_WORDS

from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ..norm_exceptions import BASE_NORMS
from ...language import Language
from ...attrs import LANG, NORM
from ...util import update_exc, add_lookups


DEFAULT_CONFIG = """
[nlp]
lang = "hu"

[nlp.lemmatizer]
@lemmatizers = "spacy.Lemmatizer.v1"
data_paths = {"@lookups": "spacy-lookups-data.hu"}
"""


class HungarianDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters[LANG] = lambda text: "hu"
    lex_attr_getters[NORM] = add_lookups(
        Language.Defaults.lex_attr_getters[NORM], BASE_NORMS
    )
    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)
    stop_words = STOP_WORDS
    prefixes = TOKENIZER_PREFIXES
    suffixes = TOKENIZER_SUFFIXES
    infixes = TOKENIZER_INFIXES
    token_match = TOKEN_MATCH


class Hungarian(Language):
    lang = "hu"
    Defaults = HungarianDefaults
    default_config = Config().from_str(DEFAULT_CONFIG)


__all__ = ["Hungarian"]
