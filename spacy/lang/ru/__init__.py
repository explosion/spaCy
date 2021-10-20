from typing import Optional
from thinc.api import Model

from .stop_words import STOP_WORDS
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .lex_attrs import LEX_ATTRS
from .lemmatizer import RussianLemmatizer
from ...language import Language, BaseDefaults


class RussianDefaults(BaseDefaults):
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    lex_attr_getters = LEX_ATTRS
    stop_words = STOP_WORDS


class Russian(Language):
    lang = "ru"
    Defaults = RussianDefaults


@Russian.factory(
    "lemmatizer",
    assigns=["token.lemma"],
    default_config={"model": None, "mode": "pymorphy2", "overwrite": False},
    default_score_weights={"lemma_acc": 1.0},
)
def make_lemmatizer(
    nlp: Language,
    model: Optional[Model],
    name: str,
    mode: str,
    overwrite: bool,
):
    return RussianLemmatizer(nlp.vocab, model, name, mode=mode, overwrite=overwrite)


__all__ = ["Russian"]
