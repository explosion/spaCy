from typing import Optional
from thinc.api import Model

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from .syntax_iterators import SYNTAX_ITERATORS
from .punctuation import TOKENIZER_PREFIXES, TOKENIZER_SUFFIXES, TOKENIZER_INFIXES
from .lemmatizer import GreekLemmatizer
from ...lookups import Lookups, load_lookups
from ...language import Language


class GreekDefaults(Language.Defaults):
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


@Greek.factory(
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
    strict = False
    if mode == "rule":
        tables = ["lemma_rules", "lemma_exc", "lemma_index"]
        strict = True
    if lookups is None:
        lookups = load_lookups(lang=nlp.lang, tables=tables, strict=strict)
    elif strict:
        for table in tables:
            assert table in lookups
    return GreekLemmatizer(nlp.vocab, model, name, mode=mode, lookups=lookups)


__all__ = ["Greek"]
