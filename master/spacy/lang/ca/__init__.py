from typing import Optional, Callable

from thinc.api import Model

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .punctuation import TOKENIZER_INFIXES, TOKENIZER_SUFFIXES, TOKENIZER_PREFIXES
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from .syntax_iterators import SYNTAX_ITERATORS
from ...language import Language, BaseDefaults
from .lemmatizer import CatalanLemmatizer


class CatalanDefaults(BaseDefaults):
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    infixes = TOKENIZER_INFIXES
    suffixes = TOKENIZER_SUFFIXES
    prefixes = TOKENIZER_PREFIXES
    stop_words = STOP_WORDS
    lex_attr_getters = LEX_ATTRS
    syntax_iterators = SYNTAX_ITERATORS


class Catalan(Language):
    lang = "ca"
    Defaults = CatalanDefaults


@Catalan.factory(
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
    return CatalanLemmatizer(
        nlp.vocab, model, name, mode=mode, overwrite=overwrite, scorer=scorer
    )


__all__ = ["Catalan"]
