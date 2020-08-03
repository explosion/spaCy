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
    tables = []
    if mode == "lookup":
        tables = ["lemma_lookup"]
    elif mode == "rule":
        tables = ["lemma_lookup", "lemma_rules", "lemma_exc", "lemma_index"]
    strict = mode in ("lookup", "rule")
    if lookups is None:
        lookups = load_lookups(lang=nlp.lang, tables=tables, strict=strict)
    elif strict:
        for table in tables:
            assert table in lookups
    return DutchLemmatizer(nlp.vocab, model, name, mode=mode, lookups=lookups)


__all__ = ["Dutch"]
