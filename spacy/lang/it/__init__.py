from typing import Optional, Callable
from thinc.api import Model

from .stop_words import STOP_WORDS
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .punctuation import TOKENIZER_PREFIXES, TOKENIZER_INFIXES
from ...language import Language, BaseDefaults
from .lemmatizer import ItalianLemmatizer


class ItalianDefaults(BaseDefaults):
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    stop_words = STOP_WORDS
    prefixes = TOKENIZER_PREFIXES
    infixes = TOKENIZER_INFIXES


class Italian(Language):
    lang = "it"
    Defaults = ItalianDefaults


@Italian.factory(
    "lemmatizer",
    assigns=["token.lemma"],
    default_config={
        "model": None,
        "mode": "pos_lookup",
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
    return ItalianLemmatizer(
        nlp.vocab, model, name, mode=mode, overwrite=overwrite, scorer=scorer
    )


__all__ = ["Italian"]
