from __future__ import unicode_literals, print_function

from os import path

from ..language import Language


class German(Language):
    lang = 'de'

    @classmethod
    def default_vocab(cls, package, get_lex_attr=None, vectors_package=None):
        vocab = super(German,cls).default_vocab(package,get_lex_attr,vectors_package)
        # set a dummy lemmatizer for now that simply returns the same string
        # until the morphology is done for German
        vocab.morphology.lemmatizer = lambda string,pos: set([string])
        return vocab
