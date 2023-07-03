from typing import Callable, Optional

from thinc.api import Model

from ...language import BaseDefaults, Language
from .lemmatizer import EnglishLemmatizer
from .lex_attrs import LEX_ATTRS
from .punctuation import TOKENIZER_INFIXES
from .stop_words import STOP_WORDS
from .syntax_iterators import SYNTAX_ITERATORS
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS


class EnglishDefaults(BaseDefaults):
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
    default_config={
        "model": None,
        "mode": "rule",
        "overwrite": False,
        "scorer": {"@scorers": "spacy.lemmatizer_scorer.v1"},
    },
    default_score_weights={"lemma_acc": 1.0},
)
def make_lemmatizer(
    nlp: Language,
    model: Optional[Model],
    name: str,
    mode: str,
    overwrite: bool,
    scorer: Optional[Callable],
):
    return EnglishLemmatizer(
        nlp.vocab, model, name, mode=mode, overwrite=overwrite, scorer=scorer
    )


__all__ = ["English"]
