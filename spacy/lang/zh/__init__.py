# coding: utf8
from __future__ import unicode_literals

from ...language import Language
from ...tokens import Doc


class Chinese(Language):
    lang = 'zh'

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
