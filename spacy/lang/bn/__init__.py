from typing import Optional
from thinc.api import Model
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .punctuation import TOKENIZER_PREFIXES, TOKENIZER_SUFFIXES, TOKENIZER_INFIXES
from .stop_words import STOP_WORDS
from ...language import Language
from ...lookups import Lookups
from ...pipeline import Lemmatizer


class BengaliDefaults(Language.Defaults):
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    prefixes = TOKENIZER_PREFIXES
    suffixes = TOKENIZER_SUFFIXES
    infixes = TOKENIZER_INFIXES
    stop_words = STOP_WORDS


class Bengali(Language):
    lang = "bn"
    Defaults = BengaliDefaults


@Bengali.factory(
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
    lookups = Lemmatizer.load_lookups(nlp.lang, mode, lookups)
    return Lemmatizer(nlp.vocab, model, name, mode=mode, lookups=lookups)


__all__ = ["Bengali"]
