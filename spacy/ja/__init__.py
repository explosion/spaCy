# encoding: utf8
from __future__ import unicode_literals, print_function

from os import path

from ..language import Language
from ..attrs import LANG
from ..tokens import Doc

from .language_data import *


class Japanese(Language):
    lang = 'ja'

    def make_doc(self, text):
        try:
            from janome.tokenizer import Tokenizer
        except ImportError:
            raise ImportError("The Japanese tokenizer requires the Janome library: "
                              "https://github.com/mocobeta/janome")
        words = [x.surface for x in Tokenizer().tokenize(text)]
        return Doc(self.vocab, words=words, spaces=[False]*len(words))
