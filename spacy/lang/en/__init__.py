from typing import Optional

from thinc.api import Model

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from .syntax_iterators import SYNTAX_ITERATORS
from .punctuation import TOKENIZER_INFIXES
from .lemmatizer import EnglishLemmatizer
from ...language import Language
from ...lookups import Lookups, load_lookups


class EnglishDefaults(Language.Defaults):
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    infixes = TOKENIZER_INFIXES
    lex_attr_getters = LEX_ATTRS
    syntax_iterators = SYNTAX_ITERATORS
    stop_words = STOP_WORDS


class English(Language):
    lang = "en"
    Defaults = EnglishDefaults


@English.factory(
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
        tables = ["lemma_rules", "lemma_exc", "lemma_index"]
    strict = mode in ("rule", "lookup")
    if lookups is None:
        lookups = load_lookups(lang=nlp.lang, tables=tables, strict=strict)
    elif strict:
        for table in tables:
            assert table in lookups
    return EnglishLemmatizer(nlp.vocab, model, name, mode=mode, lookups=lookups)


__all__ = ["English"]
