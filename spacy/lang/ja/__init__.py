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

class JapaneseCharacterSegmenter(object):
    def __init__(self, vocab):
        self.vocab = vocab

    def __call__(self, text):
        words = []
        spaces = []
        doc = self.tokenizer(text)
        for token in self.tokenizer(text):
            words.extend(list(token.text))
            spaces.extend([False]*len(token.text))
            spaces[-1] = bool(token.whitespace_)
        return Doc(self.vocab, words=words, spaces=spaces)


class JapaneseDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters[LANG] = lambda text: 'ja'
    use_janome = True

    @classmethod
    def create_tokenizer(cls, nlp=None):
        if cls.use_janome:
            return JapaneseTokenizer(cls, nlp)
        else:
            return JapaneseCharacterSegmenter(cls, nlp.vocab)


class Japanese(Language):
    lang = 'ja'
    Defaults = JapaneseDefaults

    def make_doc(self, text):
        return self.tokenizer(text)


__all__ = ['Japanese']
