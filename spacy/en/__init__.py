from __future__ import unicode_literals
from os import path
import re

from .. import orth
from ..vocab import Vocab
from ..tokenizer import Tokenizer
from ..syntax.parser import GreedyParser
from ..tokens import Tokens
from .pos import EnPosTagger
from .pos import POS_TAGS
from .attrs import get_flags


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

    Provides a tokenizer, lexicon, part-of-speech tagger and parser.

    Keyword args:
        data_dir (unicode):
            A path to a directory, from which to load the pipeline.

            By default, data is installed within the spaCy package directory. So
            if no data_dir is specified, spaCy attempts to load from a
            directory named "data" that is a sibling of the spacy/en/__init__.py
            file.  You can find the location of this file by running:

                $ python -c "import spacy.en; print spacy.en.__file__"

            To prevent any data files from being loaded, pass data_dir=None. This
            is useful if you want to construct a lexicon, which you'll then save
            for later loading.
    """
    def __init__(self, data_dir=''):
        if data_dir == '':
            data_dir = LOCAL_DATA_DIR
        self._data_dir = data_dir
        self.vocab = Vocab(data_dir=path.join(data_dir, 'vocab') if data_dir else None,
                           get_lex_props=get_lex_props)
        tag_names = list(POS_TAGS.keys())
        tag_names.sort()
        if data_dir is None:
            tok_rules = {}
            prefix_re = None
            suffix_re = None
            infix_re = None
            self.has_parser_model = False
            self.has_tagger_model = False
        else:
            tok_data_dir = path.join(data_dir, 'tokenizer')
            tok_rules, prefix_re, suffix_re, infix_re = read_lang_data(tok_data_dir)
            prefix_re = re.compile(prefix_re)
            suffix_re = re.compile(suffix_re)
            infix_re = re.compile(infix_re)
            self.has_parser_model = path.exists(path.join(self._data_dir, 'deps'))
            self.has_tagger_model = path.exists(path.join(self._data_dir, 'pos'))

        self.tokenizer = Tokenizer(self.vocab, tok_rules, prefix_re,
                                   suffix_re, infix_re,
                                   POS_TAGS, tag_names)
        # These are lazy-loaded
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

    def __call__(self, text, tag=True, parse=parse_if_model_present):
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
        tokens = self.tokenizer(text)
        if parse == -1 and tag == False:
            parse = False
        elif parse == -1 and not self.has_parser_model:
            parse = False
        if tag and self.has_tagger_model:
            self.tagger(tokens)
        if parse == True and not self.has_parser_model:
            msg = ("Receive parse=True, but parser model not found.\n\n"
                  "Run:\n"
                  "$ python -m spacy.en.download\n"
                  "To install the model.")
            raise IOError(msg)
        if parse and self.has_parser_model:
            self.parser(tokens)
        return tokens

    @property
    def tags(self):
        """List of part-of-speech tag names."""
        return self.tagger.tag_names
