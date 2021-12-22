from .stop_words import STOP_WORDS
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .lex_attrs import LEX_ATTRS
from ..tokenizer_exceptions import BASE_EXCEPTIONS

from ...language import Language, BaseDefaults
from ...attrs import LANG
from ...util import update_exc


class BulgarianDefaults(BaseDefaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters[LANG] = lambda text: "bg"

    lex_attr_getters.update(LEX_ATTRS)

    stop_words = STOP_WORDS
    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)


class Bulgarian(Language):
    lang = "bg"
    Defaults = BulgarianDefaults


__all__ = ["Bulgarian"]
