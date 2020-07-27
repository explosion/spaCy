from typing import Callable
from thinc.api import Config

from .punctuation import TOKENIZER_PREFIXES, TOKENIZER_INFIXES
from .punctuation import TOKENIZER_SUFFIXES
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from .lemmatizer import PolishLemmatizer
from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ...lookups import load_lookups
from ...language import Language
from ...util import registry


DEFAULT_CONFIG = """
[nlp]

[nlp.lemmatizer]
@lemmatizers = "spacy.pl.PolishLemmatizer"
"""

TOKENIZER_EXCEPTIONS = {
    exc: val for exc, val in BASE_EXCEPTIONS.items() if not exc.endswith(".")
}


@registry.lemmatizers("spacy.pl.PolishLemmatizer")
def create_lemmatizer() -> Callable[[Language], PolishLemmatizer]:
    # fmt: off
    tables = [
        "lemma_lookup_adj", "lemma_lookup_adp", "lemma_lookup_adv",
        "lemma_lookup_aux", "lemma_lookup_noun", "lemma_lookup_num",
        "lemma_lookup_part", "lemma_lookup_pron", "lemma_lookup_verb"
    ]
    # fmt: on

    def lemmatizer_factory(nlp: Language) -> PolishLemmatizer:
        lookups = load_lookups(lang=nlp.lang, tables=tables)
        return PolishLemmatizer(lookups=lookups)

    return lemmatizer_factory


class PolishDefaults(Language.Defaults):
    config = Config().from_str(DEFAULT_CONFIG)
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    prefixes = TOKENIZER_PREFIXES
    infixes = TOKENIZER_INFIXES
    suffixes = TOKENIZER_SUFFIXES
    lex_attr_getters = LEX_ATTRS
    stop_words = STOP_WORDS


class Polish(Language):
    lang = "pl"
    Defaults = PolishDefaults


__all__ = ["Polish"]
