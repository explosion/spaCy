from __future__ import absolute_import
from os import path
from warnings import warn
import io

try:
    import ujson as json
except ImportError:
    import json

from .tokenizer import Tokenizer
from .vocab import Vocab
from .syntax.parser import Parser
from .tagger import Tagger
from .matcher import Matcher
from .serialize.packer import Packer
from . import attrs
from . import orth
from .syntax.ner import BiluoPushDown
from .syntax.arc_eager import ArcEager

from . import util
from .attrs import TAG, DEP, ENT_IOB, ENT_TYPE, HEAD


class Language(object):
    lang = None

    @staticmethod
    def lower(string):
        return string.lower()

    @staticmethod
    def norm(string):
        return string
    
    @staticmethod
    def shape(string):
        return orth.word_shape(string)

    @staticmethod
    def prefix(string):
        return string[0]

    @staticmethod
    def suffix(string):
        return string[-3:]

    @staticmethod
    def prob(string):
        return -30

    @staticmethod
    def cluster(string):
        return 0

    @staticmethod
    def is_alpha(string):
        return orth.is_alpha(string)

    @staticmethod
    def is_ascii(string):
        return orth.is_ascii(string)

    @staticmethod
    def is_digit(string):
        return string.isdigit()

    @staticmethod
    def is_lower(string):
        return orth.is_lower(string)

    @staticmethod
    def is_punct(string):
        return orth.is_punct(string)

    @staticmethod
    def is_space(string):
        return string.isspace()

    @staticmethod
    def is_title(string):
        return orth.is_title(string)

    @staticmethod
    def is_upper(string):
        return orth.is_upper(string)

    @staticmethod
    def like_url(string):
        return orth.like_url(string)

    @staticmethod
    def like_num(string):
        return orth.like_number(string)

    @staticmethod
    def like_email(string):
        return orth.like_email(string)

    @staticmethod
    def is_stop(string):
        return 0

    @classmethod
    def default_lex_attrs(cls):
        return {
            attrs.LOWER: cls.lower,
            attrs.NORM: cls.norm,
            attrs.SHAPE: cls.shape,
            attrs.PREFIX: cls.prefix,
            attrs.SUFFIX: cls.suffix,
            attrs.CLUSTER: cls.cluster,
            attrs.PROB: lambda string: -10.0,
    
            attrs.IS_ALPHA: cls.is_alpha,
            attrs.IS_ASCII: cls.is_ascii,
            attrs.IS_DIGIT: cls.is_digit,
            attrs.IS_LOWER: cls.is_lower,
            attrs.IS_PUNCT: cls.is_punct,
            attrs.IS_SPACE: cls.is_space,
            attrs.IS_TITLE: cls.is_title,
            attrs.IS_UPPER: cls.is_upper,
            attrs.LIKE_URL: cls.like_url,
            attrs.LIKE_NUM: cls.like_num,
            attrs.LIKE_EMAIL: cls.like_email,
            attrs.IS_STOP: cls.is_stop,
            attrs.IS_OOV: lambda string: True
        }

    @classmethod
    def default_dep_labels(cls):
        return {0: {'ROOT': True}}

    @classmethod
    def default_ner_labels(cls):
        return {0: {'PER': True, 'LOC': True, 'ORG': True, 'MISC': True}}

    @classmethod
    def default_vocab(cls, package, get_lex_attr=None):
        if get_lex_attr is None:
            get_lex_attr = cls.default_lex_attrs()
        return Vocab.load(package, get_lex_attr=get_lex_attr)

    @classmethod
    def default_parser(cls, package, vocab):
        data_dir = package.dir_path('deps')
        if data_dir and path.exists(data_dir):
            return Parser.from_dir(data_dir, vocab.strings, ArcEager)

    @classmethod
    def default_entity(cls, package, vocab):
        data_dir = package.dir_path('ner')
        if data_dir and path.exists(data_dir):
            return Parser.from_dir(data_dir, vocab.strings, BiluoPushDown)

    def __init__(self,
        via=None,
        data_dir=None,
        vocab=None,
        tokenizer=None,
        tagger=None,
        parser=None,
        entity=None,
        matcher=None,
        serializer=None,
        load_vectors=True):
        """
           a model can be specified:

           1) by calling a Language subclass
             - spacy.en.English()

           2) by calling a Language subclass with via (previously: data_dir)
             - spacy.en.English('my/model/root')
             - spacy.en.English(via='my/model/root')

           3) by package name
             - spacy.load('en_default')
             - spacy.load('en_default==1.0.0')

           4) by package name with a relocated package base
             - spacy.load('en_default', via='/my/package/root')
             - spacy.load('en_default==1.0.0', via='/my/package/root')

           5) by package object
             - spacy.en.English(package)
        """

        if data_dir is not None and via is None:
            warn("Use of data_dir is deprecated, use via instead.", DeprecationWarning)
            via = data_dir

        if via is None:
            package = util.get_package_by_name()
        else:
            package = util.get_package(via)

        if load_vectors is not True:
            warn("load_vectors is deprecated", DeprecationWarning)
        if vocab in (None, True):
            vocab = Vocab.load(package, get_lex_attr=self.default_lex_attrs())
        self.vocab = vocab
        if tokenizer in (None, True):
            tokenizer = Tokenizer.load(package, self.vocab)
        self.tokenizer = tokenizer
        if tagger in (None, True):
            tagger = Tagger.load(package, self.vocab)
        self.tagger = tagger
        if entity in (None, True):
            entity = self.default_entity(package, self.vocab)
        self.entity = entity
        if parser in (None, True):
            parser = self.default_parser(package, self.vocab)
        self.parser = parser
        if matcher in (None, True):
            matcher = Matcher.load(package, self.vocab)
        self.matcher = matcher

    def __reduce__(self):
        args = (
            None, # data_dir
            None, # model
            self.vocab,
            self.tokenizer,
            self.tagger,
            self.parser,
            self.entity,
            self.matcher
        )
        return (self.__class__, args, None, None)

    def __call__(self, text, tag=True, parse=True, entity=True):
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
        if self.matcher and entity:
            self.matcher(tokens)
        if self.parser and parse:
            self.parser(tokens)
        if self.entity and entity:
            self.entity(tokens)
        return tokens

    def end_training(self, data_dir=None):
        if data_dir is None:
            data_dir = self.data_dir
        self.parser.model.end_training()
        self.parser.model.dump(path.join(data_dir, 'deps', 'model'))
        self.entity.model.end_training()
        self.entity.model.dump(path.join(data_dir, 'ner', 'model'))
        self.tagger.model.end_training()
        self.tagger.model.dump(path.join(data_dir, 'pos', 'model'))

        strings_loc = path.join(data_dir, 'vocab', 'strings.json')
        with io.open(strings_loc, 'w', encoding='utf8') as file_:
            self.vocab.strings.dump(file_)

        with open(path.join(data_dir, 'vocab', 'serializer.json'), 'w') as file_:
            file_.write(
                json.dumps([
                    (TAG, list(self.tagger.freqs[TAG].items())),
                    (DEP, list(self.parser.moves.freqs[DEP].items())),
                    (ENT_IOB, list(self.entity.moves.freqs[ENT_IOB].items())),
                    (ENT_TYPE, list(self.entity.moves.freqs[ENT_TYPE].items())),
                    (HEAD, list(self.parser.moves.freqs[HEAD].items()))]))
