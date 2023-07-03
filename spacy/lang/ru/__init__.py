from typing import Callable, Optional

from thinc.api import Model

from ...language import BaseDefaults, Language
from ..punctuation import (
    COMBINING_DIACRITICS_TOKENIZER_INFIXES,
    COMBINING_DIACRITICS_TOKENIZER_SUFFIXES,
)
from .lemmatizer import RussianLemmatizer
from .lex_attrs import LEX_ATTRS
from .stop_words import STOP_WORDS
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS


class RussianDefaults(BaseDefaults):
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    lex_attr_getters = LEX_ATTRS
    stop_words = STOP_WORDS
    suffixes = COMBINING_DIACRITICS_TOKENIZER_SUFFIXES
    infixes = COMBINING_DIACRITICS_TOKENIZER_INFIXES


class Russian(Language):
    lang = "ru"
    Defaults = RussianDefaults


@Russian.factory(
    "lemmatizer",
    assigns=["token.lemma"],
    default_config={
        "model": None,
        "mode": "pymorphy3",
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
    return RussianLemmatizer(
        nlp.vocab, model, name, mode=mode, overwrite=overwrite, scorer=scorer
    )


__all__ = ["Russian"]
