from __future__ import unicode_literals
from os import path

from .. import orth
from ..vocab import Vocab
from ..tokenizer import Tokenizer
from ..syntax.parser import GreedyParser
from ..tokens import Tokens
from ..morphology import Morphologizer
from .lemmatizer import Lemmatizer
from .pos import EnPosTagger
from .pos import POS_TAGS
from .attrs import get_flags


def get_lex_props(string):
    return {'flags': get_flags(string), 'dense': 1}


class English(object):
    def __init__(self, data_dir=None, pos_tag=True, parse=False):
        if data_dir is None:
            data_dir = path.join(path.dirname(__file__), 'data')
        self.vocab = Vocab.from_dir(data_dir, get_lex_props=get_lex_props)
        for pos_str in POS_TAGS:
            _ = self.vocab.strings.pos_tags[pos_str]
        self.tokenizer = Tokenizer.from_dir(self.vocab, data_dir)
        if pos_tag:
            morph = Morphologizer(self.vocab.strings, POS_TAGS,
                                  Lemmatizer(path.join(data_dir, 'wordnet')))
            self.pos_tagger = EnPosTagger(data_dir, morph)
        else:
            self.pos_tagger = None
        if parse:
            self.parser = GreedyParser(data_dir)
        else:
            self.parser = None

    def __call__(self, text, pos_tag=True, parse=True):
        tokens = self.tokenizer.tokenize(text)
        if self.pos_tagger and pos_tag:
            self.pos_tagger(tokens)
        if self.parser and parse:
            self.parser.parse(tokens)
        return tokens
