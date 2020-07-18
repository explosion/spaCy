from thinc.api import Config

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ..norm_exceptions import BASE_NORMS
from ...util import update_exc, add_lookups, registry
from ...lemmatizer import create_lookups
from ...language import Language
from ...attrs import LANG, NORM
from .lemmatizer import UkrainianLemmatizer


DEFAULT_CONFIG = """
[nlp]
lang = "uk"

[nlp.lemmatizer]
@lemmatizers = "spacy.UkrainianLemmatizer.v1"
"""


@registry.lemmatizers("spacy.UkrainianLemmatizer.v1")
def create_ukrainian_lemmatizer():
    def lemmatizer_factory(nlp):
        lookups = create_lookups(nlp.lang)
        return UkrainianLemmatizer(lookups=lookups)

    return lemmatizer_factory


class UkrainianDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters[LANG] = lambda text: "uk"
    lex_attr_getters[NORM] = add_lookups(
        Language.Defaults.lex_attr_getters[NORM], BASE_NORMS
    )
    lex_attr_getters.update(LEX_ATTRS)
    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)
    stop_words = STOP_WORDS


class Ukrainian(Language):
    lang = "uk"
    Defaults = UkrainianDefaults
    default_config = Config().from_str(DEFAULT_CONFIG)


__all__ = ["Ukrainian"]
