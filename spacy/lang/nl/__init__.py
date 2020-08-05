from typing import Optional

from thinc.api import Model

from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .punctuation import TOKENIZER_PREFIXES, TOKENIZER_INFIXES
from .punctuation import TOKENIZER_SUFFIXES
from .lemmatizer import DutchLemmatizer
from ...lookups import Lookups, load_lookups
from ...language import Language
from ...pipeline.lemmatizer import LOOKUPS_TABLES_CONFIG
from ...pipeline.lemmatizer import load_lemmatizer_lookups
from ...util import registry


class DutchDefaults(Language.Defaults):
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    prefixes = TOKENIZER_PREFIXES
    infixes = TOKENIZER_INFIXES
    suffixes = TOKENIZER_SUFFIXES
    lex_attr_getters = LEX_ATTRS
    stop_words = STOP_WORDS


class Dutch(Language):
    lang = "nl"
    Defaults = DutchDefaults


@Dutch.factory(
    "lemmatizer",
    assigns=["token.lemma"],
    default_config={"model": None, "mode": "rule", "lookups": None},
    scores=["lemma_acc"],
    default_score_weights={"lemma_acc": 1.0},
)
def make_lemmatizer(
    nlp: Language,
    model: Optional[Model],
    name: str,
    mode: str,
    lookups: Optional[Lookups],
):
    config = dict(LOOKUPS_TABLES_CONFIG)
    config["rules"] = ["lemma_lookup", "lemma_rules", "lemma_exc", "lemma_index"]
    lookups = load_lemmatizer_lookups(nlp.lang, mode, lookups, config=config)
    return DutchLemmatizer(nlp.vocab, model, name, mode=mode, lookups=lookups)


__all__ = ["Dutch"]
