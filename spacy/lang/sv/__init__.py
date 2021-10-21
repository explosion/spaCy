from typing import Optional
from thinc.api import Model
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from .syntax_iterators import SYNTAX_ITERATORS
from ...language import Language, BaseDefaults
from ...pipeline import Lemmatizer


# Punctuation stolen from Danish
from ..da.punctuation import TOKENIZER_INFIXES, TOKENIZER_SUFFIXES


class SwedishDefaults(BaseDefaults):
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    infixes = TOKENIZER_INFIXES
    suffixes = TOKENIZER_SUFFIXES
    lex_attr_getters = LEX_ATTRS
    syntax_iterators = SYNTAX_ITERATORS
    stop_words = STOP_WORDS


class Swedish(Language):
    lang = "sv"
    Defaults = SwedishDefaults


@Swedish.factory(
    "lemmatizer",
    assigns=["token.lemma"],
    default_config={"model": None, "mode": "rule", "overwrite": False},
    default_score_weights={"lemma_acc": 1.0},
)
def make_lemmatizer(
    nlp: Language, model: Optional[Model], name: str, mode: str, overwrite: bool
):
    return Lemmatizer(nlp.vocab, model, name, mode=mode, overwrite=overwrite)


__all__ = ["Swedish"]
