# encoding: utf8
from __future__ import unicode_literals, print_function

from ...language import Language
from ...attrs import LANG
from ...tokens import Doc
from ...tokenizer import Tokenizer


class JapaneseTokenizer(object):
    def __init__(self, cls, nlp=None):
        self.vocab = nlp.vocab if nlp is not None else cls.create_vocab(nlp)
        try:
            from janome.tokenizer import Tokenizer
        except ImportError:
            raise ImportError("The Japanese tokenizer requires the Janome "
                              "library: https://github.com/mocobeta/janome")
        self.tokenizer = Tokenizer()

    def __call__(self, text):
        words = [x.surface for x in self.tokenizer.tokenize(text)]
        return Doc(self.vocab, words=words, spaces=[False]*len(words))


class JapaneseDefaults(Language.Defaults):
    @classmethod
    def create_tokenizer(cls, nlp=None):
        return JapaneseTokenizer(cls, nlp)


class Japanese(Language):
    lang = 'ja'
    Defaults = JapaneseDefaults

    def make_doc(self, text):
        return self.tokenizer(text)


__all__ = ['Japanese']
