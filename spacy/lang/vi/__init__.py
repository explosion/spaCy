# coding: utf8
from __future__ import unicode_literals

from ...attrs import LANG, NORM
from ..norm_exceptions import BASE_NORMS
from ...language import Language
from ...tokens import Doc
from .stop_words import STOP_WORDS
from ...util import update_exc, add_lookups
from .lex_attrs import LEX_ATTRS
#from ..tokenizer_exceptions import BASE_EXCEPTIONS
#from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS


class VietnameseDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters[LANG] = lambda text: 'vi'  # for pickling
    # add more norm exception dictionaries here
    lex_attr_getters[NORM] = add_lookups(Language.Defaults.lex_attr_getters[NORM], BASE_NORMS)

    # overwrite functions for lexical attributes
    lex_attr_getters.update(LEX_ATTRS)

    # merge base exceptions and custom tokenizer exceptions
    #tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)
    stop_words = STOP_WORDS
    use_pyvi = True

class Vietnamese(Language):
    lang = 'vi'
    Defaults = VietnameseDefaults  # override defaults

    def make_doc(self, text):
        if self.Defaults.use_pyvi:
            try:
                from pyvi import ViTokenizer
            except ImportError:
                msg = ("Pyvi not installed. Either set Vietnamese.use_pyvi = False, "
                       "or install it https://pypi.python.org/pypi/pyvi")
                raise ImportError(msg)
            words, spaces = ViTokenizer.spacy_tokenize(text)
            return Doc(self.vocab, words=words, spaces=spaces)
        else:
            words = []
            spaces = []
            doc = self.tokenizer(text)
            for token in self.tokenizer(text):
                words.extend(list(token.text))
                spaces.extend([False]*len(token.text))
                spaces[-1] = bool(token.whitespace_)
            return Doc(self.vocab, words=words, spaces=spaces)

__all__ = ['Vietnamese']
