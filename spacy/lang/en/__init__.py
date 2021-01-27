from typing import Optional
from thinc.api import Model

from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS
from .syntax_iterators import SYNTAX_ITERATORS
from .punctuation import TOKENIZER_INFIXES
from .lemmatizer import EnglishLemmatizer
from ...language import Language


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
    default_config={"model": None, "mode": "rule", "overwrite": False},
    default_score_weights={"lemma_acc": 1.0},
)
def make_lemmatizer(
    nlp: Language, model: Optional[Model], name: str, mode: str, overwrite: bool
):
    return EnglishLemmatizer(nlp.vocab, model, name, mode=mode, overwrite=overwrite)


__all__ = ["English"]
