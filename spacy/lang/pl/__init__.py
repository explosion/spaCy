from typing import Optional

from thinc.api import Model

from .punctuation import TOKENIZER_PREFIXES, TOKENIZER_INFIXES
from .punctuation import TOKENIZER_SUFFIXES
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from .lemmatizer import PolishLemmatizer
from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ...lookups import Lookups, load_lookups
from ...language import Language
from ...pipeline.lemmatizer import LOOKUPS_TABLES_CONFIG
from ...pipeline.lemmatizer import load_lemmatizer_lookups


TOKENIZER_EXCEPTIONS = {
    exc: val for exc, val in BASE_EXCEPTIONS.items() if not exc.endswith(".")
}


class PolishDefaults(Language.Defaults):
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    prefixes = TOKENIZER_PREFIXES
    infixes = TOKENIZER_INFIXES
    suffixes = TOKENIZER_SUFFIXES
    lex_attr_getters = LEX_ATTRS
    stop_words = STOP_WORDS


class Polish(Language):
    lang = "pl"
    Defaults = PolishDefaults


@Polish.factory(
    "lemmatizer",
    assigns=["token.lemma"],
    default_config={"model": None, "mode": "lookup", "lookups": None},
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
    config["lookup"] = {
        "required_tables": [
            "lemma_lookup_adj",
            "lemma_lookup_adp",
            "lemma_lookup_adv",
            "lemma_lookup_aux",
            "lemma_lookup_noun",
            "lemma_lookup_num",
            "lemma_lookup_part",
            "lemma_lookup_pron",
            "lemma_lookup_verb",
        ]
    }
    lookups = load_lemmatizer_lookups(nlp.lang, mode, lookups, config=config)
    return PolishLemmatizer(nlp.vocab, model, name, mode=mode, lookups=lookups)


__all__ = ["Polish"]
