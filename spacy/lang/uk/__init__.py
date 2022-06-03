from typing import Optional, Callable

from thinc.api import Model

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from .lemmatizer import UkrainianLemmatizer
from ..punctuation import COMBINING_DIACRITICS_TOKENIZER_INFIXES
from ..punctuation import COMBINING_DIACRITICS_TOKENIZER_SUFFIXES
from ...language import Language, BaseDefaults


class UkrainianDefaults(BaseDefaults):
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    lex_attr_getters = LEX_ATTRS
    stop_words = STOP_WORDS
    suffixes = COMBINING_DIACRITICS_TOKENIZER_SUFFIXES
    infixes = COMBINING_DIACRITICS_TOKENIZER_INFIXES


class Ukrainian(Language):
    lang = "uk"
    Defaults = UkrainianDefaults


@Ukrainian.factory(
    "lemmatizer",
    assigns=["token.lemma"],
    default_config={
        "model": None,
        "mode": "pymorphy2",
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
    return UkrainianLemmatizer(
        nlp.vocab, model, name, mode=mode, overwrite=overwrite, scorer=scorer
    )


__all__ = ["Ukrainian"]
