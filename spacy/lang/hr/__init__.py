from thinc.api import Config

from .stop_words import STOP_WORDS
from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ..norm_exceptions import BASE_NORMS
from ...language import Language
from ...attrs import LANG, NORM
from ...util import update_exc, add_lookups


DEFAULT_CONFIG = """
[nlp]
lang = "hr"

[nlp.lemmatizer]
@lemmatizers = "spacy.Lemmatizer.v1"
data_paths = {"@lookups": "spacy-lookups-data.hr"}
"""


class CroatianDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters[LANG] = lambda text: "hr"
    lex_attr_getters[NORM] = add_lookups(
        Language.Defaults.lex_attr_getters[NORM], BASE_NORMS
    )
    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS)
    stop_words = STOP_WORDS


class Croatian(Language):
    lang = "hr"
    Defaults = CroatianDefaults
    default_config = Config().from_str(DEFAULT_CONFIG)


__all__ = ["Croatian"]
