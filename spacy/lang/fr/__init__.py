from typing import Callable
from thinc.api import Config

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS, TOKEN_MATCH
from .punctuation import TOKENIZER_PREFIXES, TOKENIZER_INFIXES
from .punctuation import TOKENIZER_SUFFIXES
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from .syntax_iterators import SYNTAX_ITERATORS
from .lemmatizer import FrenchLemmatizer, is_base_form
from ...lookups import load_lookups
from ...language import Language
from ...util import registry


DEFAULT_CONFIG = """
[nlp]

[nlp.lemmatizer]
@lemmatizers = "spacy.fr.FrenchLemmatizer"
"""


@registry.lemmatizers("spacy.fr.FrenchLemmatizer")
def create_lemmatizer() -> Callable[[Language], FrenchLemmatizer]:
    tables = ["lemma_rules", "lemma_index", "lemma_exc", "lemma_lookup"]

    def lemmatizer_factory(nlp: Language) -> FrenchLemmatizer:
        lookups = load_lookups(lang=nlp.lang, tables=tables)
        return FrenchLemmatizer(lookups=lookups, is_base_form=is_base_form)

    return lemmatizer_factory


class FrenchDefaults(Language.Defaults):
    config = Config().from_str(DEFAULT_CONFIG)
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    prefixes = TOKENIZER_PREFIXES
    infixes = TOKENIZER_INFIXES
    suffixes = TOKENIZER_SUFFIXES
    token_match = TOKEN_MATCH
    lex_attr_getters = LEX_ATTRS
    syntax_iterators = SYNTAX_ITERATORS
    stop_words = STOP_WORDS


class French(Language):
    lang = "fr"
    Defaults = FrenchDefaults


__all__ = ["French"]
