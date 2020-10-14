from typing import Optional

from thinc.api import Model

from .punctuation import TOKENIZER_PREFIXES, TOKENIZER_INFIXES
from .punctuation import TOKENIZER_SUFFIXES
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from .lemmatizer import PolishLemmatizer
from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ...language import Language


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
    default_config={"model": None, "mode": "pos_lookup"},
    default_score_weights={"lemma_acc": 1.0},
)
def make_lemmatizer(nlp: Language, model: Optional[Model], name: str, mode: str):
    return PolishLemmatizer(nlp.vocab, model, name, mode=mode)


__all__ = ["Polish"]
