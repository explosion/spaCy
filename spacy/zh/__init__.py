# coding: utf8
from __future__ import unicode_literals

from ..language import Language
from ..tokens import Doc
from ..vocab import Vocab
from ..tokenizer import Tokenizer
from ..attrs import LANG
from .language_data import *


class Chinese(Language):
    lang = 'zh'

    class Defaults(Language.Defaults):
        lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
        lex_attr_getters[LANG] = lambda text: 'xx'

        # override defaults
        tokenizer_exceptions = TOKENIZER_EXCEPTIONS
        tag_map = TAG_MAP
        stop_words = STOP_WORDS

    def make_doc(self, text):
        import jieba
        words = list(jieba.cut(text, cut_all=False))
        words=[x for x in words if x]
        return Doc(self.vocab, words=words, spaces=[False]*len(words))
