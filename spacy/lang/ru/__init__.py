from thinc.api import Config

from .stop_words import STOP_WORDS
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .lex_attrs import LEX_ATTRS
from .tag_map import TAG_MAP
from .lemmatizer import RussianLemmatizer
from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ...lemmatizer import create_lookups
from ...util import update_exc, registry
from ...language import Language
from ...attrs import LANG


DEFAULT_CONFIG = """
[nlp]
lang = "ru"

[nlp.lemmatizer]
@lemmatizers = "spacy.RussianLemmatizer.v1"
"""


@registry.lemmatizers("spacy.RussianLemmatizer.v1")
def create_russian_lemmatizer():
    def lemmatizer_factory(nlp):
        lookups = create_lookups(nlp.lang)
        return RussianLemmatizer(lookups=lookups)

    return lemmatizer_factory


class RussianDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters.update(LEX_ATTRS)
    lex_attr_getters[LANG] = lambda text: "ru"
    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)
    stop_words = STOP_WORDS
    tag_map = TAG_MAP


class Russian(Language):
    lang = "ru"
    Defaults = RussianDefaults
    default_config = Config().from_str(DEFAULT_CONFIG)


__all__ = ["Russian"]
