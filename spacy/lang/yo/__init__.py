# coding: utf8
from __future__ import unicode_literals

from ...attrs import LANG
from ...language import Language
from ...tokens import Doc
from ..tokenizer_exceptions import BASE_EXCEPTIONS
from .stop_words import STOP_WORDS
from .tag_map import TAG_MAP
from ...util import DummyTokenizer
from .lex_attrs import LEX_ATTRS


class YorubaDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters.update(LEX_ATTRS)
    lex_attr_getters[LANG] = lambda text: "yo"
    use_iranlowo = False
    strip_accents = False
    tokenizer_exceptions = BASE_EXCEPTIONS
    stop_words = STOP_WORDS
    tag_map = TAG_MAP
    writing_system = {"direction": "ltr", "has_case": False, "has_letters": False}


class Yoruba(Language):
    lang = "yo"
    Defaults = YorubaDefaults  # override defaults

    def make_doc(self, text):
        if self.Defaults.use_iranlowo:
            try:
                from iranlowo.tokenizer import Tokenizer
            except ImportError:
                msg = (
                    "iranlowo not installed. Either set Yoruba.use_iranlowo = False,Yoruba.strip_accents=False "
                    "or install it https://github.com/fxsjy/jieba"
                )
                raise ImportError(msg)
            words = list(Tokenizer(text).word_tokenize())
            words = [x for x in words if x]
            return Doc(self.vocab, words=words, spaces=[False] * len(words))
        else:
            words = []
            spaces = []
            for token in self.tokenizer(text):
                words.extend(list(token.text))
                spaces.extend([False] * len(token.text))
                spaces[-1] = bool(token.whitespace_)
            return Doc(self.vocab, words=words, spaces=spaces)


__all__ = ["Yoruba"]
