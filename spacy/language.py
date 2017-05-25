# coding: utf8
from __future__ import absolute_import, unicode_literals
from contextlib import contextmanager
import dill

import numpy
from thinc.neural import Model
from thinc.neural.ops import NumpyOps, CupyOps
from thinc.neural.optimizers import Adam, SGD
import random

from .tokenizer import Tokenizer
from .vocab import Vocab
from .tagger import Tagger
from .lemmatizer import Lemmatizer
from .syntax.parser import get_templates
from .syntax import nonproj
from .pipeline import NeuralDependencyParser, EntityRecognizer
from .pipeline import TokenVectorEncoder, NeuralTagger, NeuralEntityRecognizer
from .pipeline import NeuralLabeller
from .compat import json_dumps
from .attrs import IS_STOP
from .lang.punctuation import TOKENIZER_PREFIXES, TOKENIZER_SUFFIXES, TOKENIZER_INFIXES
from .lang.tokenizer_exceptions import TOKEN_MATCH
from .lang.tag_map import TAG_MAP
from .lang.lex_attrs import LEX_ATTRS
from . import util
from .scorer import Scorer


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
        'token_vectors': lambda nlp, **cfg: [TokenVectorEncoder(nlp.vocab, **cfg)],
        'tags': lambda nlp, **cfg: [NeuralTagger(nlp.vocab, **cfg)],
        'dependencies': lambda nlp, **cfg: [
            NeuralDependencyParser(nlp.vocab, **cfg),
            nonproj.deprojectivize],
        'entities': lambda nlp, **cfg: [NeuralEntityRecognizer(nlp.vocab, **cfg)],
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
    """A text-processing pipeline. Usually you'll load this once per process,
    and pass the instance around your application.

    Defaults (class): Settings, data and factory methods for creating the `nlp`
        object and processing pipeline.
    lang (unicode): Two-letter language ID, i.e. ISO code.
    """
    Defaults = BaseDefaults
    lang = None

    def __init__(self, vocab=True, make_doc=True, pipeline=None, meta={}):
        """Initialise a Language object.

        vocab (Vocab): A `Vocab` object. If `True`, a vocab is created via
            `Language.Defaults.create_vocab`.
        make_doc (callable): A function that takes text and returns a `Doc`
            object. Usually a `Tokenizer`.
        pipeline (list): A list of annotation processes or IDs of annotation,
            processes, e.g. a `Tagger` object, or `'tagger'`. IDs are looked
            up in `Language.Defaults.factories`.
        meta (dict): Custom meta data for the Language class. Is written to by
            models to add model meta data.
        RETURNS (Language): The newly constructed object.
        """
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
        flat_list = []
        for pipe in self.pipeline:
            if isinstance(pipe, list):
                flat_list.extend(pipe)
            else:
                flat_list.append(pipe)
        self.pipeline = flat_list

    def __call__(self, text, **disabled):
        """'Apply the pipeline to some text. The text can span multiple sentences,
        and can contain arbtrary whitespace. Alignment into the original string
        is preserved.

        text (unicode): The text to be processed.
        **disabled: Elements of the pipeline that should not be run.
        RETURNS (Doc): A container for accessing the annotations.

        EXAMPLE:
            >>> tokens = nlp('An example sentence. Another example sentence.')
            >>> tokens[0].text, tokens[0].head.tag_
            ('An', 'NN')
        """
        doc = self.make_doc(text)
        for proc in self.pipeline:
            name = getattr(proc, 'name', None)
            if name in disabled and not disabled[name]:
                continue
            proc(doc)
        return doc

    def update(self, docs, golds, drop=0., sgd=None, losses=None):
        """Update the models in the pipeline.

        docs (iterable): A batch of `Doc` objects.
        golds (iterable): A batch of `GoldParse` objects.
        drop (float): The droput rate.
        sgd (callable): An optimizer.
        RETURNS (dict): Results from the update.

        EXAMPLE:
            >>> with nlp.begin_training(gold, use_gpu=True) as (trainer, optimizer):
            >>>    for epoch in trainer.epochs(gold):
            >>>        for docs, golds in epoch:
            >>>            state = nlp.update(docs, golds, sgd=optimizer)
        """
        tok2vec = self.pipeline[0]
        feats = tok2vec.doc2feats(docs)
        procs = list(self.pipeline[1:])
        random.shuffle(procs)
        grads = {}
        def get_grads(W, dW, key=None):
            grads[key] = (W, dW)
        for proc in procs:
            if not hasattr(proc, 'update'):
                continue
            tokvecses, bp_tokvecses = tok2vec.model.begin_update(feats, drop=drop)
            d_tokvecses = proc.update((docs, tokvecses), golds,
                                      drop=drop, sgd=sgd, losses=losses)
            bp_tokvecses(d_tokvecses, sgd=sgd)
        for key, (W, dW) in grads.items():
            sgd(W, dW, key=key)
        # Clear the tensor variable, to free GPU memory.
        # If we don't do this, the memory leak gets pretty
        # bad, because we may be holding part of a batch.
        for doc in docs:
            doc.tensor = None

    def preprocess_gold(self, docs_golds):
        """Can be called before training to pre-process gold data. By default,
        it handles nonprojectivity and adds missing tags to the tag map.

        docs_golds (iterable): Tuples of `Doc` and `GoldParse` objects.
        YIELDS (tuple): Tuples of preprocessed `Doc` and `GoldParse` objects.
        """
        for proc in self.pipeline:
            if hasattr(proc, 'preprocess_gold'):
                docs_golds = proc.preprocess_gold(docs_golds)
        for doc, gold in docs_golds:
            yield doc, gold

    def begin_training(self, get_gold_tuples, **cfg):
        """Allocate models, pre-process training data and acquire a trainer and
        optimizer. Used as a contextmanager.

        gold_tuples (iterable): Gold-standard training data.
        **cfg: Config parameters.
        YIELDS (tuple): A trainer and an optimizer.

        EXAMPLE:
            >>> with nlp.begin_training(gold, use_gpu=True) as (trainer, optimizer):
            >>>    for epoch in trainer.epochs(gold):
            >>>        for docs, golds in epoch:
            >>>            state = nlp.update(docs, golds, sgd=optimizer)
        """
        self.pipeline.append(NeuralLabeller(self.vocab))
        # Populate vocab
        for _, annots_brackets in get_gold_tuples():
            for annots, _ in annots_brackets:
                for word in annots[1]:
                    _ = self.vocab[word]
        contexts = []
        if cfg.get('use_gpu'):
            Model.ops = CupyOps()
            Model.Ops = CupyOps
            print("Use GPU")
        for proc in self.pipeline:
            if hasattr(proc, 'begin_training'):
                context = proc.begin_training(get_gold_tuples(),
                                              pipeline=self.pipeline)
                contexts.append(context)
        optimizer = Adam(Model.ops, 0.001)
        return optimizer

    def evaluate(self, docs_golds):
        docs, golds = zip(*docs_golds)
        scorer = Scorer()
        for doc, gold in zip(self.pipe(docs), golds):
            scorer.score(doc, gold)
            doc.tensor = None
        return scorer

    @contextmanager
    def use_params(self, params, **cfg):
        """Replace weights of models in the pipeline with those provided in the
        params dictionary. Can be used as a contextmanager, in which case,
        models go back to their original weights after the block.

        params (dict): A dictionary of parameters keyed by model ID.
        **cfg: Config parameters.

        EXAMPLE:
            >>> with nlp.use_params(optimizer.averages):
            >>>     nlp.to_disk('/tmp/checkpoint')
        """
        contexts = [pipe.use_params(params) for pipe
                    in self.pipeline if hasattr(pipe, 'use_params')]
        # TODO: Having trouble with contextlib
        # Workaround: these aren't actually context managers atm.
        for context in contexts:
            try:
                next(context)
            except StopIteration:
                pass
        yield
        for context in contexts:
            try:
                next(context)
            except StopIteration:
                pass

    def pipe(self, texts, n_threads=2, batch_size=1000, **disabled):
        """Process texts as a stream, and yield `Doc` objects in order. Supports
        GIL-free multi-threading.

        texts (iterator): A sequence of texts to process.
        n_threads (int): The number of worker threads to use. If -1, OpenMP will
            decide how many to use at run time. Default is 2.
        batch_size (int): The number of texts to buffer.
        **disabled: Pipeline components to exclude.
        YIELDS (Doc): Documents in the order of the original text.

        EXAMPLE:
            >>> texts = [u'One document.', u'...', u'Lots of documents']
            >>>     for doc in nlp.pipe(texts, batch_size=50, n_threads=4):
            >>>         assert doc.is_parsed
        """
        docs = (self.make_doc(text) for text in texts)
        docs = texts
        for proc in self.pipeline:
            name = getattr(proc, 'name', None)
            if name in disabled and not disabled[name]:
                continue
            if hasattr(proc, 'pipe'):
                docs = proc.pipe(docs, n_threads=n_threads, batch_size=batch_size)
            else:
                # Apply the function, but yield the doc
                docs = _pipe(proc, docs)
        for doc in docs:
            yield doc

    def to_disk(self, path, **exclude):
        """Save the current state to a directory.

        path (unicode or Path): A path to a directory, which will be created if
            it doesn't exist. Paths may be either strings or `Path`-like objects.
        **exclude: Named attributes to prevent from being saved.

        EXAMPLE:
            >>> nlp.to_disk('/path/to/models')
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
        """Loads state from a directory. Modifies the object in place and
        returns it.

        path (unicode or Path): A path to a directory. Paths may be either
            strings or `Path`-like objects.
        **exclude: Named attributes to prevent from being loaded.
        RETURNS (Language): The modified `Language` object.

        EXAMPLE:
            >>> from spacy.language import Language
            >>> nlp = Language().from_disk('/path/to/models')
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

        **exclude: Named attributes to prevent from being serialized.
        RETURNS (bytes): The serialized form of the `Language` object.
        """
        props = dict(self.__dict__)
        for key in exclude:
            if key in props:
                props.pop(key)
        return dill.dumps(props, -1)

    def from_bytes(self, bytes_data, **exclude):
        """Load state from a binary string.

        bytes_data (bytes): The data to load from.
        **exclude: Named attributes to prevent from being loaded.
        RETURNS (Language): The `Language` object.
        """
        props = dill.loads(bytes_data)
        for key, value in props.items():
            if key not in exclude:
                setattr(self, key, value)
        return self

def _pipe(func, docs):
    for doc in docs:
        func(doc)
        yield doc
