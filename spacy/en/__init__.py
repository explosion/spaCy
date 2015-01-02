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


DATA_DIR = path.join(path.dirname(__file__), 'data')


def get_lex_props(string):
    return {'flags': get_flags(string), 'dense': 1}


class English(object):
    """The English NLP pipeline.

    Provides a tokenizer, lexicon, part-of-speech tagger and parser.

    Keyword args:
        data_dir (unicode): A path to a directory, from which to load the pipeline.
            If None, looks for a directory named "data/" in the same directory as
            the present file, i.e. path.join(path.dirname(__file__, 'data')).
            If path.join(data_dir, 'pos') exists, the tagger is loaded from it.
            If path.join(data_dir, 'deps') exists, the parser is loaded from it.
            See Pipeline Directory Structure for details.

    Attributes:
        vocab (spacy.vocab.Vocab): The lexicon.

        strings (spacy.strings.StringStore): Encode/decode strings to/from integer IDs.

        tokenizer (spacy.tokenizer.Tokenizer): The start of the pipeline.

        tagger (spacy.en.pos.EnPosTagger):
            The part-of-speech tagger, which also performs lemmatization and
            morphological analysis.

        parser (spacy.syntax.parser.GreedyParser):
            A greedy shift-reduce dependency parser.
    """
    def __init__(self, data_dir=None):
        if data_dir is None:
            data_dir = path.join(path.dirname(__file__), 'data')
        self._data_dir = data_dir
        self.vocab = Vocab(data_dir=path.join(data_dir, 'vocab'),
                           get_lex_props=get_lex_props)
        tag_names = list(POS_TAGS.keys())
        tag_names.sort()
        self.tokenizer = Tokenizer.from_dir(self.vocab, path.join(data_dir, 'tokenizer'),
                                            POS_TAGS, tag_names)
        self.strings = self.vocab.strings
        self._tagger = None
        self._parser = None

    @property
    def tagger(self):
        if self._tagger is None:
            self._tagger = EnPosTagger(self.vocab.strings, self._data_dir)
        return self._tagger

    @property
    def parser(self):
        if self._parser is None:
            self._parser = GreedyParser(path.join(self._data_dir, 'deps'))
        return self._parser

    def __call__(self, text, tag=True, parse=False):
        """Apply the pipeline to some text.
        
        Args:
            text (unicode): The text to be processed.

        Keyword args:
            tag (bool): Whether to add part-of-speech tags to the text.  This
                will also set morphological analysis and lemmas.

            parse (bool): Whether to add dependency-heads and labels to the text.

        Returns:
            tokens (spacy.tokens.Tokens):
        """
        tokens = self.tokenizer.tokenize(text)
        if tag:
            self.tagger(tokens)
        if parse:
            self.parser.parse(tokens)
        return tokens

    @property
    def tags(self):
        """List of part-of-speech tag names."""
        return self.tagger.tag_names
