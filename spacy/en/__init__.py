from __future__ import unicode_literals
from os import path
import re

from .. import orth
from ..vocab import Vocab
from ..tokenizer import Tokenizer
from ..syntax.arc_eager import ArcEager
from ..syntax.ner import BiluoPushDown
from ..syntax.parser import ParserFactory

from ..tokens import Doc
from ..multi_words import RegexMerger

from .pos import EnPosTagger
from .pos import POS_TAGS
from .attrs import get_flags
from . import regexes

from ..exceptions import ModelNotLoaded

from ..util import read_lang_data


def get_lex_props(string):
    return {
        'flags': get_flags(string),
        'length': len(string),
        'orth': string,
        'lower': string.lower(),
        'norm': string,
        'shape': orth.word_shape(string),
        'prefix': string[0],
        'suffix': string[-3:],
        'cluster': 0,
        'prob': 0,
        'sentiment': 0
    }

if_model_present = -1


class English(object):
    """The English NLP pipeline.

    Example:

        Load data from default directory:

            >>> nlp = English()
            >>> nlp = English(data_dir=u'')

        Load data from specified directory:
    
            >>> nlp = English(data_dir=u'path/to/data_directory')

        Disable (and avoid loading) parts of the processing pipeline:

            >>> nlp = English(vectors=False, parser=False, tagger=False, entity=False)
        
        Start with nothing loaded:

            >>> nlp = English(data_dir=None)
    """
    ParserTransitionSystem = ArcEager
    EntityTransitionSystem = BiluoPushDown

    def __init__(self,
      data_dir=path.join(path.dirname(__file__), 'data'),
      Tokenizer=Tokenizer.from_dir,
      Tagger=EnPosTagger,
      Parser=ParserFactory(ParserTransitionSystem),
      Entity=ParserFactory(EntityTransitionSystem),
      load_vectors=True
    ):
        
        self._data_dir = data_dir
        
        self.vocab = Vocab(data_dir=path.join(data_dir, 'vocab') if data_dir else None,
                           get_lex_props=get_lex_props, load_vectors=load_vectors,
                           pos_tags=POS_TAGS)
        if Tagger is True:
            Tagger = EnPosTagger
        if Parser is True:
            transition_system = self.ParserTransitionSystem
            Parser = lambda s, d: parser.Parser(s, d, transition_system)
        if Entity is True:
            transition_system = self.EntityTransitionSystem
            Entity = lambda s, d: parser.Parser(s, d, transition_system)

        self.tokenizer = Tokenizer(self.vocab, path.join(data_dir, 'tokenizer'))
        
        if Tagger:
            self.tagger = Tagger(self.vocab.strings, data_dir)
        else:
            self.tagger = None
        if Parser:
            self.parser = Parser(self.vocab.strings, path.join(data_dir, 'deps'))
        else:
            self.parser = None
        if Entity:
            self.entity = Entity(self.vocab.strings, path.join(data_dir, 'ner'))
        else:
            self.entity = None
        self.mwe_merger = RegexMerger([
            ('IN', 'O', regexes.MW_PREPOSITIONS_RE),
            ('CD', 'TIME', regexes.TIME_RE),
            ('NNP', 'DATE', regexes.DAYS_RE),
            ('CD', 'MONEY', regexes.MONEY_RE)])

    def __call__(self, text, tag=True, parse=True, entity=True):
        """Apply the pipeline to some text.  The text can span multiple sentences,
        and can contain arbtrary whitespace.  Alignment into the original string
        is preserved.
        
        Args:
            text (unicode): The text to be processed.

        Returns:
            tokens (spacy.tokens.Tokens):

        >>> from spacy.en import English
        >>> nlp = English()
        >>> tokens = nlp('An example sentence. Another example sentence.')
        >>> tokens[0].orth_, tokens[0].head.tag_
        ('An', 'NN')
        """
        tokens = self.tokenizer(text)
        if self.tagger and tag:
            self.tagger(tokens)
        if self.parser and parse:
            self.parser(tokens)
        if self.entity and entity:
            self.entity(tokens)
        return tokens

    @property
    def tags(self):
        """List of part-of-speech tag names."""
        return self.tagger.tag_names
