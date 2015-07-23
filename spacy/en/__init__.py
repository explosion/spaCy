from __future__ import unicode_literals
from os import path
import re
import struct
import json

from .. import orth
from ..vocab import Vocab
from ..tokenizer import Tokenizer
from ..syntax.arc_eager import ArcEager
from ..syntax.ner import BiluoPushDown
from ..syntax.parser import ParserFactory
from ..serialize.bits import BitArray

from ..tokens import Doc
from ..multi_words import RegexMerger

from .pos import EnPosTagger
from .pos import POS_TAGS
from .attrs import get_flags
from . import regexes

from ..util import read_lang_data

from ..attrs import TAG, HEAD, DEP, ENT_TYPE, ENT_IOB


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
        'prob': -22,
        'sentiment': 0
    }

if_model_present = -1
LOCAL_DATA_DIR = path.join(path.dirname(__file__), 'data')


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
      data_dir=LOCAL_DATA_DIR,
      Tokenizer=Tokenizer.from_dir,
      Tagger=EnPosTagger,
      Parser=ParserFactory(ParserTransitionSystem),
      Entity=ParserFactory(EntityTransitionSystem),
      Packer=None,
      load_vectors=True
    ):
        
        self.data_dir = data_dir
        
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
        
        if Tagger and path.exists(path.join(data_dir, 'pos')):
            self.tagger = Tagger(self.vocab.strings, data_dir)
        else:
            self.tagger = None
        if Parser and path.exists(path.join(data_dir, 'deps')):
            self.parser = Parser(self.vocab.strings, path.join(data_dir, 'deps'))
        else:
            self.parser = None
        if Entity and path.exists(path.join(data_dir, 'ner')):
            self.entity = Entity(self.vocab.strings, path.join(data_dir, 'ner'))
        else:
            self.entity = None
        if Packer:
            self.packer = Packer(self.vocab, data_dir)
        else:
            self.packer = None
        self.mwe_merger = RegexMerger([
            ('IN', 'O', regexes.MW_PREPOSITIONS_RE),
            ('CD', 'TIME', regexes.TIME_RE),
            ('NNP', 'DATE', regexes.DAYS_RE),
            ('CD', 'MONEY', regexes.MONEY_RE)])

    def __call__(self, text, tag=True, parse=True, entity=True, merge_mwes=False):
        """Apply the pipeline to some text.  The text can span multiple sentences,
        and can contain arbtrary whitespace.  Alignment into the original string
        is preserved.
        
        Args:
            text (unicode): The text to be processed.

        Returns:
            tokens (spacy.tokens.Doc):

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
        if merge_mwes and self.mwe_merger is not None:
            self.mwe_merger(tokens)
        return tokens

    def end_training(self, data_dir=None):
        if data_dir is None:
            data_dir = self.data_dir
        self.parser.model.end_training()
        self.entity.model.end_training()
        self.tagger.model.end_training()
        self.vocab.strings.dump(path.join(data_dir, 'vocab', 'strings.txt'))

        with open(path.join(data_dir, 'vocab', 'serializer.json'), 'w') as file_:
            file_.write(
                json.dumps([
                    (TAG, self.tagger.freqs[TAG].items()),
                    (DEP, self.parser.moves.freqs[DEP].items()),
                    (ENT_IOB, self.entity.moves.freqs[ENT_IOB].items()),
                    (ENT_TYPE, self.entity.moves.freqs[ENT_TYPE].items()),
                    (HEAD, self.parser.moves.freqs[HEAD].items())]))

    @property
    def tags(self):
        """Deprecated. List of part-of-speech tag names."""
        return self.tagger.tag_names
