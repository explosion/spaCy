from thinc.api import Config

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .punctuation import TOKENIZER_PREFIXES, TOKENIZER_SUFFIXES
from .punctuation import TOKENIZER_INFIXES
from .stop_words import STOP_WORDS
from .syntax_iterators import SYNTAX_ITERATORS

from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ...language import Language
from ...attrs import LANG
from ...util import update_exc


DEFAULT_CONFIG = """
[nlp]
lang = "de"

[nlp.lemmatizer]
@lemmatizers = "spacy.Lemmatizer.v1"

[nlp.lemmatizer.data_paths]
@assets = "spacy-lookups-data"
lang = ${nlp:lang}
"""


class GermanDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters[LANG] = lambda text: "de"
    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)
    prefixes = TOKENIZER_PREFIXES
    suffixes = TOKENIZER_SUFFIXES
    infixes = TOKENIZER_INFIXES
    stop_words = STOP_WORDS
    syntax_iterators = SYNTAX_ITERATORS
    single_orth_variants = [
        {"tags": ["$("], "variants": ["…", "..."]},
        {"tags": ["$("], "variants": ["-", "—", "–", "--", "---", "——"]},
    ]
    paired_orth_variants = [
        {
            "tags": ["$("],
            "variants": [("'", "'"), (",", "'"), ("‚", "‘"), ("›", "‹"), ("‹", "›")],
        },
        {
            "tags": ["$("],
            "variants": [("``", "''"), ('"', '"'), ("„", "“"), ("»", "«"), ("«", "»")],
        },
    ]


class German(Language):
    lang = "de"
    Defaults = GermanDefaults
    default_config = Config().from_str(DEFAULT_CONFIG)


__all__ = ["German"]
