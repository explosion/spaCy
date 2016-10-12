from __future__ import absolute_import
from __future__ import unicode_literals
from warnings import warn
import pathlib
from contextlib import contextmanager
import shutil

try:
    import ujson as json
except ImportError:
    import json


try:
    basestring
except NameError:
    basestring = str


from .tokenizer import Tokenizer
from .vocab import Vocab
from .syntax.parser import Parser
from .tagger import Tagger
from .matcher import Matcher
from . import attrs
from . import orth
from .syntax.ner import BiluoPushDown
from .syntax.arc_eager import ArcEager
from . import util
from .lemmatizer import Lemmatizer
from .train import Trainer

from .attrs import TAG, DEP, ENT_IOB, ENT_TYPE, HEAD, PROB, LANG, IS_STOP
from .syntax.parser import get_templates
from .syntax.nonproj import PseudoProjectivity



class BaseDefaults(object):
    def __init__(self, lang, path):
        self.path = path
        self.lang = lang
        self.lex_attr_getters = dict(self.__class__.lex_attr_getters)
        if self.path and (self.path / 'vocab' / 'oov_prob').exists():
            with (self.path / 'vocab' / 'oov_prob').open() as file_:
                oov_prob = file_.read().strip()
            self.lex_attr_getters[PROB] = lambda string: oov_prob
        self.lex_attr_getters[LANG] = lambda string: lang
        self.lex_attr_getters[IS_STOP] = lambda string: string in self.stop_words

    def Lemmatizer(self):
        return Lemmatizer.load(self.path) if self.path else Lemmatizer({}, {}, {})

    def Vectors(self):
        return True

    def Vocab(self, lex_attr_getters=True, tag_map=True,
              lemmatizer=True, serializer_freqs=True, vectors=True):
        if lex_attr_getters is True:
            lex_attr_getters = self.lex_attr_getters
        if tag_map is True:
            tag_map = self.tag_map
        if lemmatizer is True:
            lemmatizer = self.Lemmatizer()
        if vectors is True:
            vectors = self.Vectors()
        if self.path:
            return Vocab.load(self.path, lex_attr_getters=lex_attr_getters,
                              tag_map=tag_map, lemmatizer=lemmatizer,
                              serializer_freqs=serializer_freqs)
        else:
            return Vocab(lex_attr_getters=lex_attr_getters, tag_map=tag_map,
                         lemmatizer=lemmatizer, serializer_freqs=serializer_freqs)

    def Tokenizer(self, vocab, rules=None, prefix_search=None, suffix_search=None,
                  infix_finditer=None):
        if rules is None:
            rules = self.tokenizer_exceptions
        if prefix_search is None:
            prefix_search  = util.compile_prefix_regex(self.prefixes).search
        if suffix_search is None:
            suffix_search  = util.compile_suffix_regex(self.suffixes).search
        if infix_finditer is None:
            infix_finditer = util.compile_infix_regex(self.infixes).finditer
        if self.path:
            return Tokenizer.load(self.path, vocab, rules=rules,
                                  prefix_search=prefix_search,
                                  suffix_search=suffix_search,
                                  infix_finditer=infix_finditer)
        else:
            tokenizer =  Tokenizer(vocab, rules=rules,
                    prefix_search=prefix_search, suffix_search=suffix_search,
                    infix_finditer=infix_finditer)
            return tokenizer

    def Tagger(self, vocab, **cfg):
        if self.path:
            return Tagger.load(self.path / 'pos', vocab)
        else:
            return Tagger.blank(vocab, Tagger.default_templates())

    def Parser(self, vocab, **cfg):
        if self.path and (self.path / 'dep').exists():
            return Parser.load(self.path / 'dep', vocab, ArcEager)
        else:
            if 'features' not in cfg:
                cfg['features'] = self.parser_features
            if 'labels' not in cfg:
                cfg['labels'] = self.parser_labels
            return Parser.blank(vocab, ArcEager, **cfg)

    def Entity(self, vocab, **cfg):
        if self.path and (self.path / 'ner').exists():
            return Parser.load(self.path / 'ner', vocab, BiluoPushDown)
        else:
            if 'features' not in cfg:
                cfg['features'] = self.entity_features
            if 'labels' not in cfg:
                cfg['labels'] = self.entity_labels
            return Parser.blank(vocab, BiluoPushDown, **cfg)

    def Matcher(self, vocab, **cfg):
        if self.path:
            return Matcher.load(self.path, vocab)
        else:
            return Matcher(vocab)

    def Pipeline(self, nlp, **cfg):
        pipeline = [nlp.tokenizer]
        if nlp.tagger:
            pipeline.append(nlp.tagger)
        if nlp.parser:
            pipeline.append(nlp.parser)
        if nlp.entity:
            pipeline.append(nlp.entity)
        return pipeline
    
    prefixes = tuple()

    suffixes = tuple()

    infixes = tuple()
 
    tag_map = {}

    tokenizer_exceptions = {}
   
    parser_labels = {0: {'': True}, 1: {'': True}, 2: {'ROOT': True, 'nmod': True},
                         3: {'ROOT': True, 'nmod': True}, 4: {'ROOT': True}}
 

    entity_labels = {
                        0: {'': True},
                        1: {'PER': True, 'LOC': True, 'ORG': True, 'MISC': True},
                        2: {'PER': True, 'LOC': True, 'ORG': True, 'MISC': True},
                        3: {'PER': True, 'LOC': True, 'ORG': True, 'MISC': True},
                        4: {'PER': True, 'LOC': True, 'ORG': True, 'MISC': True},
                        5: {'': True}
                     }

    parser_features = get_templates('parser')
    
    entity_features = get_templates('ner')

    stop_words = set()

    lex_attr_getters = {
        attrs.LOWER: lambda string: string.lower(),
        attrs.NORM: lambda string: string,
        attrs.SHAPE: orth.word_shape,
        attrs.PREFIX: lambda string: string[0],
        attrs.SUFFIX: lambda string: string[-3:],
        attrs.CLUSTER: lambda string: 0,
        attrs.IS_ALPHA: orth.is_alpha,
        attrs.IS_ASCII: orth.is_ascii,
        attrs.IS_DIGIT: lambda string: string.isdigit(),
        attrs.IS_LOWER: orth.is_lower,
        attrs.IS_PUNCT: orth.is_punct,
        attrs.IS_SPACE: lambda string: string.isspace(),
        attrs.IS_TITLE: orth.is_title,
        attrs.IS_UPPER: orth.is_upper,
        attrs.IS_BRACKET: orth.is_bracket,
        attrs.IS_QUOTE: orth.is_quote,
        attrs.IS_LEFT_PUNCT: orth.is_left_punct,
        attrs.IS_RIGHT_PUNCT: orth.is_right_punct,
        attrs.LIKE_URL: orth.like_url,
        attrs.LIKE_NUM: orth.like_number,
        attrs.LIKE_EMAIL: orth.like_email,
        attrs.IS_STOP: lambda string: False,
        attrs.IS_OOV: lambda string: True
    }


class Language(object):
    '''A text-processing pipeline. Usually you'll load this once per process, and
    pass the instance around your program.
    '''
    Defaults = BaseDefaults
    lang = None

    @classmethod
    @contextmanager
    def train(cls, path, gold_tuples, *configs):
        if isinstance(path, basestring):
            path = pathlib.Path(path)
        tagger_cfg, parser_cfg, entity_cfg = configs
        dep_model_dir = path / 'dep'
        ner_model_dir = path / 'ner'
        pos_model_dir = path / 'pos'
        if dep_model_dir.exists():
            shutil.rmtree(str(dep_model_dir))
        if ner_model_dir.exists():
            shutil.rmtree(str(ner_model_dir))
        if pos_model_dir.exists():
            shutil.rmtree(str(pos_model_dir))
        dep_model_dir.mkdir()
        ner_model_dir.mkdir()
        pos_model_dir.mkdir()

        if parser_cfg['pseudoprojective']:
            # preprocess training data here before ArcEager.get_labels() is called
            gold_tuples = PseudoProjectivity.preprocess_training_data(gold_tuples)

        parser_cfg['labels'] = ArcEager.get_labels(gold_tuples)
        entity_cfg['labels'] = BiluoPushDown.get_labels(gold_tuples)

        with (dep_model_dir / 'config.json').open('wb') as file_:
            json.dump(parser_cfg, file_)
        with (ner_model_dir / 'config.json').open('wb') as file_:
            json.dump(entity_cfg, file_)
        with (pos_model_dir / 'config.json').open('wb') as file_:
            json.dump(tagger_cfg, file_)

        self = cls(
                path=path,
                vocab=False,
                tokenizer=False,
                tagger=False,
                parser=False,
                entity=False,
                matcher=False,
                serializer=False,
                vectors=False,
                pipeline=False)

        self.defaults.parser_labels = parser_cfg['labels']
        self.defaults.entity_labels = entity_cfg['labels']

        self.vocab = self.defaults.Vocab()
        self.tokenizer = self.defaults.Tokenizer(self.vocab)
        self.tagger = self.defaults.Tagger(self.vocab, **tagger_cfg)
        self.parser = self.defaults.Parser(self.vocab, **parser_cfg)
        self.entity = self.defaults.Entity(self.vocab, **entity_cfg)
        self.pipeline = self.defaults.Pipeline(self)
        yield Trainer(self, gold_tuples)
        self.end_training()

    def __init__(self,
        path=None,
        vocab=True,
        tokenizer=True,
        tagger=True,
        parser=True,
        entity=True,
        matcher=True,
        serializer=True,
        vectors=True,
        pipeline=True,
        defaults=True,
        data_dir=None):
        """
        A model can be specified:

        1) by calling a Language subclass
            - spacy.en.English()

        2) by calling a Language subclass with data_dir
            - spacy.en.English('my/model/root')
            - spacy.en.English(data_dir='my/model/root')

        3) by package name
            - spacy.load('en_default')
            - spacy.load('en_default==1.0.0')

        4) by package name with a relocated package base
            - spacy.load('en_default', via='/my/package/root')
            - spacy.load('en_default==1.0.0', via='/my/package/root')
        """
        if data_dir is not None and path is None:
            warn("'data_dir' argument now named 'path'. Doing what you mean.")
            path = data_dir
        if isinstance(path, basestring):
            path = pathlib.Path(path)
        if path is None:
            path = util.match_best_version(self.lang, '', util.get_data_path())
        self.path = path
        defaults = defaults if defaults is not True else self.get_defaults(self.path)
        
        self.defaults = defaults
        self.vocab     = vocab if vocab is not True else defaults.Vocab(vectors=vectors)
        self.tokenizer = tokenizer if tokenizer is not True else defaults.Tokenizer(self.vocab)
        self.tagger    = tagger if tagger is not True else defaults.Tagger(self.vocab)
        self.entity    = entity if entity is not True else defaults.Entity(self.vocab)
        self.parser    = parser if parser is not True else defaults.Parser(self.vocab)
        self.matcher   = matcher if matcher is not True else defaults.Matcher(self.vocab)
        if pipeline in (None, False):
            self.pipeline = []
        elif pipeline is True:
            self.pipeline = defaults.Pipeline(self)
        else:
            self.pipeline = pipeline(self)

    def __reduce__(self):
        args = (
            self.path, 
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
        doc = self.pipeline[0](text)
        if self.entity and entity:
            # Add any of the entity labels already set, in case we don't have them.
            for token in doc:
                if token.ent_type != 0:
                    self.entity.add_label(token.ent_type)
        skip = {self.tagger: not tag, self.parser: not parse, self.entity: not entity}
        for proc in self.pipeline[1:]:
            if proc and not skip.get(proc):
                proc(doc)
        return doc

    def pipe(self, texts, tag=True, parse=True, entity=True, n_threads=2,
            batch_size=1000):
        skip = {self.tagger: not tag, self.parser: not parse, self.entity: not entity}
        stream = self.pipeline[0].pipe(texts,
            n_threads=n_threads, batch_size=batch_size)
        for proc in self.pipeline[1:]:
            if proc and not skip.get(proc):
                if hasattr(proc, 'pipe'):
                    stream = proc.pipe(stream, n_threads=n_threads, batch_size=batch_size)
                else:
                    stream = (proc(item) for item in stream)
        for doc in stream:
            yield doc

    def end_training(self, path=None):
        if path is None:
            path = self.path
        elif isinstance(path, basestring):
            path = pathlib.Path(path)
        
        if self.tagger:
            self.tagger.model.end_training()
            self.tagger.model.dump(str(path / 'pos' / 'model'))
        if self.parser:
            self.parser.model.end_training()
            self.parser.model.dump(str(path / 'dep' / 'model'))
        if self.entity:
            self.entity.model.end_training()
            self.entity.model.dump(str(path / 'ner' / 'model'))
        
        strings_loc = path / 'vocab' / 'strings.json'
        with strings_loc.open('w', encoding='utf8') as file_:
            self.vocab.strings.dump(file_)
        self.vocab.dump(path / 'vocab' / 'lexemes.bin')

        if self.tagger:
            tagger_freqs = list(self.tagger.freqs[TAG].items())
        else:
            tagger_freqs = []
        if self.parser:
            dep_freqs = list(self.parser.moves.freqs[DEP].items())
            head_freqs = list(self.parser.moves.freqs[HEAD].items())
        else:
            dep_freqs = []
            head_freqs = []
        if self.entity:
            entity_iob_freqs = list(self.entity.moves.freqs[ENT_IOB].items())
            entity_type_freqs = list(self.entity.moves.freqs[ENT_TYPE].items())
        else:
            entity_iob_freqs = []
            entity_type_freqs = []
        with (path / 'vocab' / 'serializer.json').open('wb') as file_:
            file_.write(
                json.dumps([
                    (TAG, tagger_freqs),
                    (DEP, dep_freqs),
                    (ENT_IOB, entity_iob_freqs),
                    (ENT_TYPE, entity_type_freqs),
                    (HEAD, head_freqs)
                ]))

    def get_defaults(self, path):
        return self.Defaults(self.lang, path)
