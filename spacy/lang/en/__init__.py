from typing import Callable
from thinc.api import Config

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from .syntax_iterators import SYNTAX_ITERATORS
from .lemmatizer import is_base_form
from .punctuation import TOKENIZER_INFIXES
from ...language import Language
from ...lemmatizer import OldLemmatizer
from ...lookups import load_lookups
from ...util import registry


DEFAULT_CONFIG = """
[nlp]

"""


@registry.lemmatizers("spacy.en.EnglishLemmatizer")
def create_lemmatizer() -> Callable[[Language], OldLemmatizer]:
    tables = ["lemma_lookup", "lemma_rules", "lemma_exc", "lemma_index"]

    def lemmatizer_factory(nlp: Language) -> OldLemmatizer:
        lookups = load_lookups(lang=nlp.lang, tables=tables)
        return OldLemmatizer(lookups=lookups, is_base_form=is_base_form)

    return lemmatizer_factory


class EnglishDefaults(Language.Defaults):
    config = Config().from_str(DEFAULT_CONFIG)
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    infixes = TOKENIZER_INFIXES
    lex_attr_getters = LEX_ATTRS
    syntax_iterators = SYNTAX_ITERATORS
    stop_words = STOP_WORDS


class English(Language):
    lang = "en"
    Defaults = EnglishDefaults


__all__ = ["English"]
