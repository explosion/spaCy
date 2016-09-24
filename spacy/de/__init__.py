from __future__ import unicode_literals, print_function

from os import path

from ..language import Language
from ..vocab import Vocab
from ..attrs import LANG


class German(Language):
    lang = 'de'
    
    class Defaults(Language.Defaults):
        def Vocab(self, vectors=None, lex_attr_getters=None):
            if lex_attr_getters is None:
                lex_attr_getters = dict(self.lex_attr_getters)
            if vectors is None:
                vectors = self.Vectors()
            # set a dummy lemmatizer for now that simply returns the same string
            # until the morphology is done for German
            return Vocab.load(self.path, get_lex_attr=lex_attr_getters, vectors=vectors,
                              lemmatizer=False)

        stop_words = set()
