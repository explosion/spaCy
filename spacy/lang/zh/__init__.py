# coding: utf8
from __future__ import unicode_literals

from ...attrs import LANG
from ...language import Language
from ...tokens import Doc
from .tag_map import TAG_MAP
from .stop_words import STOP_WORDS
from ...util import update_exc
from ..tokenizer_exceptions import BASE_EXCEPTIONS
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS


class ChineseDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters[LANG] = lambda text: 'zh'  # for pickling
    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS, TOKENIZER_EXCEPTIONS)
    tag_map = TAG_MAP
    stop_words = STOP_WORDS


class Chinese(Language):
    lang = 'zh'
    Defaults = ChineseDefaults  # override defaults

    def make_doc(self, text):
        try:
            import jieba
        except ImportError:
            raise ImportError("The Chinese tokenizer requires the Jieba library: "
                              "https://github.com/fxsjy/jieba")
        words = list(jieba.cut(text, cut_all=False))
        words = [x for x in words if x]
        return Doc(self.vocab, words=words, spaces=[False]*len(words))


__all__ = ['Chinese']
