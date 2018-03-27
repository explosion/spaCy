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

    # add dummy methods for to_bytes, from_bytes, to_disk and from_disk to
    # allow serialization (see #1557)
    def to_bytes(self, **exclude):
        return b''

    def from_bytes(self, bytes_data, **exclude):
        return self

    def to_disk(self, path, **exclude):
        return None

    def from_disk(self, path, **exclude):
        return self


class JapaneseDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters[LANG] = lambda text: 'ja'

    @classmethod
    def create_tokenizer(cls, nlp=None):
        return JapaneseTokenizer(cls, nlp)


class Japanese(Language):
    lang = 'ja'
    Defaults = JapaneseDefaults

    def make_doc(self, text):
        return self.tokenizer(text)


__all__ = ['Japanese']
