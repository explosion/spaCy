from __future__ import unicode_literals
from os import path

from .. import orth
from ..vocab import Vocab
from ..tokenizer import Tokenizer
from ..syntax.parser import GreedyParser
from ..tokens import Tokens
from .pos import EnPosTagger
from .pos import POS_TAGS
from .attrs import get_flags


def get_lex_props(string):
    return {'flags': get_flags(string), 'dense': 1}


class English(object):
    def __init__(self, data_dir=None, tag=True, parse=False):
        if data_dir is None:
            data_dir = path.join(path.dirname(__file__), 'data')
        self.vocab = Vocab(data_dir=data_dir, get_lex_props=get_lex_props)
        self.tokenizer = Tokenizer.from_dir(self.vocab, data_dir)
        self.tagger = EnPosTagger(self.vocab.strings, data_dir) if tag else None
        self.parser = GreedyParser(path.join(data_dir, 'deps')) if parse else None
        self.strings = self.vocab.strings

    def __call__(self, text, tag=True, parse=True):
        tokens = self.tokenizer.tokenize(text)
        if self.tagger and tag:
            self.tagger(tokens)
        if self.parser and parse:
            self.parser.parse(tokens)
        return tokens

    @property
    def tags(self):
        if self.tagger is None:
            return []
        else:
            return self.tagger.tag_names
