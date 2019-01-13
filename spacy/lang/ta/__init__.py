# import language-specific data
from .stop_words import STOP_WORDS
from .lex_attrs import LEX_ATTRS

from ..tokenizer_exceptions import BASE_EXCEPTIONS
from ...language import Language
from ...attrs import LANG
from ...util import update_exc

# create Defaults class in the module scope (necessary for pickling!)
class TamilDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters[LANG] = lambda text: 'ta' # language ISO code

    # optional: replace flags with custom functions, e.g. like_num()
    lex_attr_getters.update(LEX_ATTRS)

# create actual Language class
class Tamil(Language):
    lang = 'ta' # language ISO code
    Defaults = TamilDefaults # override defaults

# set default export – this allows the language class to be lazy-loaded
__all__ = ['Tamil']
