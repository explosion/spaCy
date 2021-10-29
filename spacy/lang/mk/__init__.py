from typing import Optional
from thinc.api import Model
from .lemmatizer import MacedonianLemmatizer
from .stop_words import STOP_WORDS
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .lex_attrs import LEX_ATTRS
from ..tokenizer_exceptions import BASE_EXCEPTIONS

from ...language import Language, BaseDefaults
from ...attrs import LANG
from ...util import update_exc
from ...lookups import Lookups


class MacedonianDefaults(BaseDefaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters[LANG] = lambda text: "mk"

    # Optional: replace flags with custom functions, e.g. like_num()
    lex_attr_getters.update(LEX_ATTRS)

    # Merge base exceptions and custom tokenizer exceptions
    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)
    stop_words = STOP_WORDS

    @classmethod
    def create_lemmatizer(cls, nlp=None, lookups=None):
        if lookups is None:
            lookups = Lookups()
        return MacedonianLemmatizer(lookups)


class Macedonian(Language):
    lang = "mk"
    Defaults = MacedonianDefaults


@Macedonian.factory(
    "lemmatizer",
    assigns=["token.lemma"],
    default_config={"model": None, "mode": "rule", "overwrite": False},
    default_score_weights={"lemma_acc": 1.0},
)
def make_lemmatizer(
    nlp: Language, model: Optional[Model], name: str, mode: str, overwrite: bool
):
    return MacedonianLemmatizer(nlp.vocab, model, name, mode=mode, overwrite=overwrite)


__all__ = ["Macedonian"]
