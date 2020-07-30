from typing import Callable
from thinc.api import Config

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from .lemmatizer import GreekLemmatizer
from .syntax_iterators import SYNTAX_ITERATORS
from .punctuation import TOKENIZER_PREFIXES, TOKENIZER_SUFFIXES, TOKENIZER_INFIXES
from ...lookups import load_lookups
from ...language import Language
from ...util import registry


DEFAULT_CONFIG = """
[nlp]

"""


@registry.lemmatizers("spacy.el.GreekLemmatizer")
def create_lemmatizer() -> Callable[[Language], GreekLemmatizer]:
    tables = ["lemma_index", "lemma_exc", "lemma_rules"]

    def lemmatizer_factory(nlp: Language) -> GreekLemmatizer:
        lookups = load_lookups(lang=nlp.lang, tables=tables)
        return GreekLemmatizer(lookups=lookups)

    return lemmatizer_factory


class GreekDefaults(Language.Defaults):
    config = Config().from_str(DEFAULT_CONFIG)
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    prefixes = TOKENIZER_PREFIXES
    suffixes = TOKENIZER_SUFFIXES
    infixes = TOKENIZER_INFIXES
    lex_attr_getters = LEX_ATTRS
    stop_words = STOP_WORDS
    syntax_iterators = SYNTAX_ITERATORS


class Greek(Language):
    lang = "el"
    Defaults = GreekDefaults


__all__ = ["Greek"]
