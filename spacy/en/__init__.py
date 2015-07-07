from __future__ import unicode_literals
from os import path
import re

from .. import orth
from ..vocab import Vocab
from ..tokenizer import Tokenizer
from ..syntax.parser import Parser
from ..syntax.arc_eager import ArcEager
from ..syntax.ner import BiluoPushDown
from ..tokens import Tokens
from ..multi_words import RegexMerger

from .pos import EnPosTagger
from .pos import POS_TAGS
from .attrs import get_flags
from . import regexes


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

    def __init__(self, data_dir='', Tokenizer=True, Vectors=True, Parser=True,
                 Tagger=True, Entity=True, Senser=True, load_vectors=True):
        if data_dir == '':
            data_dir = LOCAL_DATA_DIR
        # TODO: Deprecation warning
        if load_vectors is False:
            vectors = False

        self.vocab = Vocab(data_dir=path.join(data_dir, 'vocab') if data_dir else None,
                           get_lex_props=get_lex_props, vectors=Vectors)

        if Tokenizer is True:
            Tokenizer = tokenizer.Tokenizer
        if Tagger is True:
            Tagger = pos.EnPosTagger
        if Parser is True:
            transition_system = self.ParserTransitionSystem
            Parser = lambda s, d: parser.Parser(s, d, transition_system
        if Entity is True:
            transition_system = self.EntityTransitionSystem
            Entity = lambda s, d: parser.Parser(s, d, transition_system)
        if Senser is True:
            Senser = wsd.SuperSenseTagger

        self.tokenizer = Tokenizer(self.vocab, data_dir) if Tokenizer else None
        self.tagger = Tagger(self.vocab.strings, data_dir) if Tagger else None
        self.parser = Parser(self.vocab.strings, data_dir) if Parser else None
        self.entity = Entity(self.vocab.strings, data_dir) if Entity else None
        self.senser = Senser(self.vocab.strings, data_dir) if Senser else None

        self._data_dir = data_dir
        tag_names = list(POS_TAGS.keys())
        tag_names.sort()
        if data_dir is None:
            tok_rules = {}
            prefix_re = None
            suffix_re = None
            infix_re = None
        else:
            tok_data_dir = path.join(data_dir, 'tokenizer')
            tok_rules, prefix_re, suffix_re, infix_re = read_lang_data(tok_data_dir)
            prefix_re = re.compile(prefix_re)
            suffix_re = re.compile(suffix_re)
            infix_re = re.compile(infix_re)

        self.tokenizer = Tokenizer(self.vocab, tok_rules, prefix_re,
                                   suffix_re, infix_re,
                                   POS_TAGS, tag_names)

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
        elif parse == -1 and not self.has_parser_model:
            parse = False
        if entity == -1 and tag == False:
            entity = False
        elif entity == -1 and not self.has_entity_model:
            entity = False
        if tag and self.has_tagger_model:
            self.tagger(tokens)
        if parse == True and not self.has_parser_model:
            msg = ("Received parse=True, but parser model not found.\n\n"
                  "Run:\n"
                  "$ python -m spacy.en.download\n"
                  "To install the model.")
            raise IOError(msg)
        if entity == True and not self.has_entity_model:
            msg = ("Received entity=True, but entity model not found.\n\n"
                  "Run:\n"
                  "$ python -m spacy.en.download\n"
                  "To install the model.")
            raise IOError(msg)

        if parse and self.has_parser_model:
            self.parser(tokens)
        if entity and self.has_entity_model:
            self.entity(tokens)
        if merge_mwes and self.mwe_merger is not None:
            self.mwe_merger(tokens)
        return tokens

    @property
    def tags(self):
        """List of part-of-speech tag names."""
        return self.tagger.tag_names
