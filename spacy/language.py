# coding: utf8
from __future__ import absolute_import, unicode_literals
from contextlib import contextmanager
import dill

from .tokenizer import Tokenizer
from .vocab import Vocab
from .tagger import Tagger
from .lemmatizer import Lemmatizer
from .train import Trainer
from .syntax.parser import get_templates
from .syntax.nonproj import PseudoProjectivity
from .pipeline import NeuralDependencyParser, EntityRecognizer
from .pipeline import TokenVectorEncoder, NeuralTagger, NeuralEntityRecognizer
from .compat import json_dumps
from .attrs import IS_STOP
from .lang.punctuation import TOKENIZER_PREFIXES, TOKENIZER_SUFFIXES, TOKENIZER_INFIXES
from .lang.tokenizer_exceptions import TOKEN_MATCH
from .lang.tag_map import TAG_MAP
from .lang.lex_attrs import LEX_ATTRS
from . import util


class BaseDefaults(object):
    @classmethod
    def create_lemmatizer(cls, nlp=None):
        return Lemmatizer(cls.lemma_index, cls.lemma_exc, cls.lemma_rules)

    @classmethod
    def create_vocab(cls, nlp=None):
        lemmatizer = cls.create_lemmatizer(nlp)
        lex_attr_getters = dict(cls.lex_attr_getters)
        # This is messy, but it's the minimal working fix to Issue #639.
        lex_attr_getters[IS_STOP] = lambda string: string.lower() in cls.stop_words
        vocab = Vocab(lex_attr_getters=lex_attr_getters, tag_map=cls.tag_map,
                      lemmatizer=lemmatizer)
        for tag_str, exc in cls.morph_rules.items():
            for orth_str, attrs in exc.items():
                vocab.morphology.add_special_case(tag_str, orth_str, attrs)
        return vocab

    @classmethod
    def create_tokenizer(cls, nlp=None):
        rules = cls.tokenizer_exceptions
        token_match = cls.token_match
        prefix_search = util.compile_prefix_regex(cls.prefixes).search \
                        if cls.prefixes else None
        suffix_search = util.compile_suffix_regex(cls.suffixes).search \
                        if cls.suffixes else None
        infix_finditer = util.compile_infix_regex(cls.infixes).finditer \
                         if cls.infixes else None
        vocab = nlp.vocab if nlp is not None else cls.create_vocab(nlp)
        return Tokenizer(vocab, rules=rules,
                         prefix_search=prefix_search, suffix_search=suffix_search,
                         infix_finditer=infix_finditer, token_match=token_match)

    @classmethod
    def create_tagger(cls, nlp=None, **cfg):
        if nlp is None:
            return NeuralTagger(cls.create_vocab(nlp), **cfg)
        else:
            return NeuralTagger(nlp.vocab, **cfg)

    @classmethod
    def create_parser(cls, nlp=None, **cfg):
        if nlp is None:
            return NeuralDependencyParser(cls.create_vocab(nlp), **cfg)
        else:
            return NeuralDependencyParser(nlp.vocab, **cfg)

    @classmethod
    def create_entity(cls, nlp=None, **cfg):
        if nlp is None:
            return NeuralEntityRecognizer(cls.create_vocab(nlp), **cfg)
        else:
            return NeuralEntityRecognizer(nlp.vocab, **cfg)

    @classmethod
    def create_pipeline(cls, nlp=None):
        meta = nlp.meta if nlp is not None else {}
        # Resolve strings, like "cnn", "lstm", etc
        pipeline = []
        for entry in cls.pipeline:
            factory = cls.Defaults.factories[entry]
            pipeline.append(factory(nlp, **meta.get(entry, {})))
        return pipeline

    factories = {
        'make_doc': create_tokenizer,
        'token_vectors': lambda nlp, **cfg: TokenVectorEncoder(nlp.vocab, **cfg),
        'tags': lambda nlp, **cfg: NeuralTagger(nlp.vocab, **cfg),
        'dependencies': lambda nlp, **cfg: NeuralDependencyParser(nlp.vocab, **cfg),
        'entities': lambda nlp, **cfg: NeuralEntityRecognizer(nlp.vocab, **cfg),
    }

    token_match = TOKEN_MATCH
    prefixes = tuple(TOKENIZER_PREFIXES)
    suffixes = tuple(TOKENIZER_SUFFIXES)
    infixes = tuple(TOKENIZER_INFIXES)
    tag_map = dict(TAG_MAP)
    tokenizer_exceptions = {}
    parser_features = get_templates('parser')
    entity_features = get_templates('ner')
    tagger_features = Tagger.feature_templates # TODO -- fix this
    stop_words = set()
    lemma_rules = {}
    lemma_exc = {}
    lemma_index = {}
    morph_rules = {}
    lex_attr_getters = LEX_ATTRS


class Language(object):
    """
    A text-processing pipeline. Usually you'll load this once per process, and
    pass the instance around your program.
    """
    Defaults = BaseDefaults
    lang = None

    def __init__(self, vocab=True, make_doc=True, pipeline=None, meta={}):
        self.meta = dict(meta)

        if vocab is True:
            factory = self.Defaults.create_vocab
            vocab = factory(self, **meta.get('vocab', {}))
        self.vocab = vocab
        if make_doc is True:
            factory = self.Defaults.create_tokenizer
            make_doc = factory(self, **meta.get('tokenizer', {}))
        self.make_doc = make_doc
        if pipeline is True:
            self.pipeline = self.Defaults.create_pipeline(self)
        elif pipeline:
            self.pipeline = list(pipeline)
            # Resolve strings, like "cnn", "lstm", etc
            for i, entry in enumerate(self.pipeline):
                if entry in self.Defaults.factories:
                    factory = self.Defaults.factories[entry]
                    self.pipeline[i] = factory(self, **meta.get(entry, {}))
        else:
            self.pipeline = []

    def __call__(self, text, state=None, **disabled):
        """
        Apply the pipeline to some text.  The text can span multiple sentences,
        and can contain arbtrary whitespace.  Alignment into the original string
        is preserved.

        Args:
            text (unicode): The text to be processed.
            state: Arbitrary

        Returns:
            doc (Doc): A container for accessing the annotations.

        Example:
            >>> from spacy.en import English
            >>> nlp = English()
            >>> tokens = nlp('An example sentence. Another example sentence.')
            >>> tokens[0].orth_, tokens[0].head.tag_
            ('An', 'NN')
        """
        doc = self.make_doc(text)
        for proc in self.pipeline:
            name = getattr(proc, 'name', None)
            if name in disabled and not disabled[name]:
                continue
            state = proc(doc, state=state)
        return doc

    def update(self, docs, golds, state=None, drop=0., sgd=None):
        grads = {}
        def get_grads(W, dW, key=None):
            grads[key] = (W, dW)
        state = {} if state is None else state
        for process in self.pipeline:
            if hasattr(process, 'update'):
                state = process.update(docs, golds,
                            state=state,
                            drop=drop,
                            sgd=sgd)
            else:
                process(docs, state=state)
        if sgd is not None:
            for key, (W, dW) in grads.items():
                sgd(W, dW, key=key)
        return state

    @contextmanager
    def begin_training(self, gold_tuples, **cfg):
        # Populate vocab
        for _, annots_brackets in gold_tuples:
            for annots, _ in annots_brackets:
                for word in annots[1]:
                    _ = self.vocab[word]
        # Handle crossing dependencies
        gold_tuples = PseudoProjectivity.preprocess_training_data(gold_tuples)
        contexts = []
        for proc in self.pipeline:
            if hasattr(proc, 'begin_training'):
                context = proc.begin_training(gold_tuples,
                                              pipeline=self.pipeline)
                contexts.append(context)
        trainer = Trainer(self, gold_tuples, **cfg)
        yield trainer, trainer.optimizer

    def pipe(self, texts, n_threads=2, batch_size=1000, **disabled):
        """
        Process texts as a stream, and yield Doc objects in order.

        Supports GIL-free multi-threading.

        Arguments:
            texts (iterator)
            tag (bool)
            parse (bool)
            entity (bool)
        """
        stream = ((self.make_doc(text), None) for text in texts)
        for proc in self.pipeline:
            name = getattr(proc, 'name', None)
            if name in disabled and not disabled[name]:
                continue

            if hasattr(proc, 'pipe'):
                stream = proc.pipe(stream, n_threads=n_threads, batch_size=batch_size)
            else:
                stream = (proc(doc, state) for doc, state in stream)
        for doc, state in stream:
            yield doc

    def to_disk(self, path, **exclude):
        """Save the current state to a directory.

        Args:
            path: A path to a directory, which will be created if it doesn't
                    exist. Paths may be either strings or pathlib.Path-like
                    objects.
            **exclude: Prevent named attributes from being saved.
        """
        path = util.ensure_path(path)
        if not path.exists():
            path.mkdir()
        if not path.is_dir():
            raise IOError("Output path must be a directory")
        props = {}
        for name, value in self.__dict__.items():
            if name in exclude:
                continue
            if hasattr(value, 'to_disk'):
                value.to_disk(path / name)
            else:
                props[name] = value
        with (path / 'props.pickle').open('wb') as file_:
            dill.dump(props, file_)

    def from_disk(self, path, **exclude):
        """Load the current state from a directory.

        Args:
            path: A path to a directory. Paths may be either strings or
                pathlib.Path-like objects.
            **exclude: Prevent named attributes from being saved.
        """
        path = util.ensure_path(path)
        for name in path.iterdir():
            if name not in exclude and hasattr(self, str(name)):
                getattr(self, name).from_disk(path / name)
        with (path / 'props.pickle').open('rb') as file_:
            bytes_data = file_.read()
        self.from_bytes(bytes_data, **exclude)
        return self

    def to_bytes(self, **exclude):
        """Serialize the current state to a binary string.

        Args:
            path: A path to a directory. Paths may be either strings or
                pathlib.Path-like objects.
            **exclude: Prevent named attributes from being serialized.
        """
        props = dict(self.__dict__)
        for key in exclude:
            if key in props:
                props.pop(key)
        return dill.dumps(props, -1)

    def from_bytes(self, bytes_data, **exclude):
        """Load state from a binary string.

        Args:
            bytes_data (bytes): The data to load from.
            **exclude: Prevent named attributes from being loaded.
        """
        props = dill.loads(bytes_data)
        for key, value in props.items():
            if key not in exclude:
                setattr(self, key, value)
        return self

