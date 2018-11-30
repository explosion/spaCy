# coding: utf8
from __future__ import unicode_literals


from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ..norm_exceptions import BASE_NORMS
from ...language import Language
from ...attrs import LANG, NORM
from ...util import update_exc, add_lookups


class MultiLanguageDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters[LANG] = lambda text: "xx"
    lex_attr_getters[NORM] = add_lookups(
        Language.Defaults.lex_attr_getters[NORM], BASE_NORMS
    )
    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS)


class MultiLanguage(Language):
    """Language class to be used for models that support multiple languages.
    This module allows models to specify their language ID as 'xx'.
    """

    lang = "xx"
    Defaults = MultiLanguageDefaults


__all__ = ["MultiLanguage"]
