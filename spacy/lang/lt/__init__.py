from thinc.api import Config

from .punctuation import TOKENIZER_INFIXES, TOKENIZER_SUFFIXES
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS

from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ..norm_exceptions import BASE_NORMS
from ...language import Language
from ...attrs import LANG, NORM
from ...util import update_exc, add_lookups


DEFAULT_CONFIG = """
[nlp]
lang = "lt"

[nlp.lemmatizer]
@lemmatizers = "spacy.Lemmatizer.v1"

[nlp.lemmatizer.data_paths]
@assets = "spacy-lookups-data"
lang = ${nlp:lang}
"""


class LithuanianDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters[LANG] = lambda text: "lt"
    lex_attr_getters[NORM] = add_lookups(
        Language.Defaults.lex_attr_getters[NORM], BASE_NORMS
    )
    lex_attr_getters.update(LEX_ATTRS)

    infixes = TOKENIZER_INFIXES
    suffixes = TOKENIZER_SUFFIXES
    mod_base_exceptions = {
        exc: val for exc, val in BASE_EXCEPTIONS.items() if not exc.endswith(".")
    }
    del mod_base_exceptions["8)"]
    tokenizer_exceptions = update_exc(mod_base_exceptions, TOKENIZER_EXCEPTIONS)
    stop_words = STOP_WORDS


class Lithuanian(Language):
    lang = "lt"
    Defaults = LithuanianDefaults
    default_config = Config().from_str(DEFAULT_CONFIG)


__all__ = ["Lithuanian"]
