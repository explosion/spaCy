# coding: utf8
from __future__ import unicode_literals

from .lemmatizer import MacedonianLemmatizer
from .stop_words import STOP_WORDS
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .lex_attrs import LEX_ATTRS
from ..tokenizer_exceptions import BASE_EXCEPTIONS
from .morph_rules import MORPH_RULES

from ...language import Language
from ...attrs import LANG
from ...util import update_exc
from ...lookups import Lookups


class MacedonianDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters[LANG] = lambda text: "mk"

    # Optional: replace flags with custom functions, e.g. like_num()
    lex_attr_getters.update(LEX_ATTRS)

    # Merge base exceptions and custom tokenizer exceptions
    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)
    stop_words = STOP_WORDS
    morph_rules = MORPH_RULES

    @classmethod
    def create_lemmatizer(cls, nlp=None, lookups=None):
        if lookups is None:
            lookups = Lookups()
        return MacedonianLemmatizer(lookups)


class Macedonian(Language):
    lang = "mk"
    Defaults = MacedonianDefaults


__all__ = ["Macedonian"]
