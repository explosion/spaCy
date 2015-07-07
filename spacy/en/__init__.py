from __future__ import unicode_literals
from os import path
import re

from .. import orth
from ..vocab import Vocab
from ..tokenizer import Tokenizer
from ..syntax import parser
from ..syntax.arc_eager import ArcEager
from ..syntax.ner import BiluoPushDown
from ..tokens import Tokens
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


LOCAL_DATA_DIR = path.join(path.dirname(__file__), 'data')

parse_if_model_present = -1


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

    Keyword args:
        data_dir (unicode):
            A path to a directory from which to load the pipeline;
            or '', to load default; or None, to load nothing.

        Tokenizer (bool or callable):
            desc

        Vectors (bool or callable):
            desc

        Parser (bool or callable):
            desc

        Tagger (bool or callable):
            desc

        Entity (bool or callable):
            desc

        Senser (bool or callable):
            desc
    """
    ParserTransitionSystem = ArcEager
    EntityTransitionSystem = BiluoPushDown

    def __init__(self, data_dir='', Tokenizer=Tokenizer.from_dir, Vectors=True,
                 Parser=True, Tagger=EnPosTagger, Entity=True, load_vectors=True):
        if data_dir == '':
            data_dir = LOCAL_DATA_DIR
        self._data_dir = data_dir
        
        # TODO: Deprecation warning
        if load_vectors is False:
            vectors = False

        self.vocab = Vocab(data_dir=path.join(data_dir, 'vocab') if data_dir else None,
                           get_lex_props=get_lex_props, load_vectors=Vectors,
                           pos_tags=POS_TAGS)
        if Tagger is True:
            Tagger = EnPosTagger
        if Parser is True:
            transition_system = self.ParserTransitionSystem
            Parser = lambda s, d: parser.Parser(s, d, transition_system)
        if Entity is True:
            transition_system = self.EntityTransitionSystem
            Entity = lambda s, d: parser.Parser(s, d, transition_system)

        if Tokenizer: 
            self.tokenizer = Tokenizer(self.vocab, path.join(data_dir, 'tokenizer'))
        else:
            self.tokenizer = None
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

    def __call__(self, text, tag=True, parse=parse_if_model_present,
                 entity=parse_if_model_present, merge_mwes=False):
        """Apply the pipeline to some text.  The text can span multiple sentences,
        and can contain arbtrary whitespace.  Alignment into the original string

        The tagger and parser are lazy-loaded the first time they are required.
        Loading the parser model usually takes 5-10 seconds.

        Args:
            text (unicode): The text to be processed.

        Keyword args:
            tag (bool): Whether to add part-of-speech tags to the text.  Also
                sets morphological analysis and lemmas.

            parse (True, False, -1): Whether to add labelled syntactic dependencies.

              -1 (default) is "guess": It will guess True if tag=True and the
                model has been installed.

        Returns:
            tokens (spacy.tokens.Tokens):

        >>> from spacy.en import English
        >>> nlp = English()
        >>> tokens = nlp('An example sentence. Another example sentence.')
        >>> tokens[0].orth_, tokens[0].head.tag_
        ('An', 'NN')
        """
        if parse == True and tag == False:
            msg = ("Incompatible arguments: tag=False, parse=True"
                   "Part-of-speech tags are required for parsing.")
            raise ValueError(msg)
        if entity == True and tag == False:
            msg = ("Incompatible arguments: tag=False, entity=True"
                   "Part-of-speech tags are required for entity recognition.")
            raise ValueError(msg)

        tokens = self.tokenizer(text)
        if parse == -1 and tag == False:
            parse = False
        elif parse == -1 and self.parser is None:
            parse = False
        if entity == -1 and tag == False:
            entity = False
        elif entity == -1 and self.entity is None:
            entity = False
        if tag:
            ModelNotLoaded.check(self.tagger, 'tagger')
            self.tagger(tokens)
        if parse:
            ModelNotLoaded.check(self.parser, 'parser')
            self.parser(tokens)
        if entity:
            ModelNotLoaded.check(self.entity, 'entity')
            self.entity(tokens)

        if merge_mwes and self.mwe_merger is not None:
            self.mwe_merger(tokens)
        return tokens

    @property
    def tags(self):
        """List of part-of-speech tag names."""
        return self.tagger.tag_names
