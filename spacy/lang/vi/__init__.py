# coding: utf8
from __future__ import unicode_literals

from ...attrs import LANG, NORM
from ..norm_exceptions import BASE_NORMS
from ...language import Language
from ...tokens import Doc
from .stop_words import STOP_WORDS
from ...util import add_lookups
from .lex_attrs import LEX_ATTRS


class VietnameseDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters[LANG] = lambda text: "vi"  # for pickling
    lex_attr_getters[NORM] = add_lookups(
        Language.Defaults.lex_attr_getters[NORM], BASE_NORMS
    )
    lex_attr_getters.update(LEX_ATTRS)
    stop_words = STOP_WORDS
    use_pyvi = True


class Vietnamese(Language):
    lang = "vi"
    Defaults = VietnameseDefaults  # override defaults

    def make_doc(self, text):
        if self.Defaults.use_pyvi:
            try:
                from pyvi import ViTokenizer
            except ImportError:
                msg = (
                    "Pyvi not installed. Either set Vietnamese.use_pyvi = False, "
                    "or install it https://pypi.python.org/pypi/pyvi"
                )
                raise ImportError(msg)
            words, spaces = ViTokenizer.spacy_tokenize(text)
            return Doc(self.vocab, words=words, spaces=spaces)
        else:
            words = []
            spaces = []
            for token in self.tokenizer(text):
                words.extend(list(token.text))
                spaces.extend([False] * len(token.text))
                spaces[-1] = bool(token.whitespace_)
            return Doc(self.vocab, words=words, spaces=spaces)


__all__ = ["Vietnamese"]
