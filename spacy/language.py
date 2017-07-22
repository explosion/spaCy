# coding: utf8
from __future__ import absolute_import, unicode_literals
from contextlib import contextmanager
import dill

import numpy
from thinc.neural import Model
from thinc.neural.ops import NumpyOps, CupyOps
from thinc.neural.optimizers import Adam, SGD
import random
import ujson
from collections import OrderedDict

from .tokenizer import Tokenizer
from .vocab import Vocab
from .tagger import Tagger
from .lemmatizer import Lemmatizer
from .syntax.parser import get_templates
from .syntax import nonproj

from .pipeline import NeuralDependencyParser, EntityRecognizer
from .pipeline import TokenVectorEncoder, NeuralTagger, NeuralEntityRecognizer
from .pipeline import NeuralLabeller
from .pipeline import SimilarityHook
from .pipeline import TextCategorizer
from . import about

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
    def create_pipeline(cls, nlp=None, disable=tuple()):
        meta = nlp.meta if nlp is not None else {}
        # Resolve strings, like "cnn", "lstm", etc
        pipeline = []
        for entry in cls.pipeline:
            if entry in disable or getattr(entry, 'name', entry) in disable:
                continue
            factory = cls.Defaults.factories[entry]
            pipeline.append(factory(nlp, **meta.get(entry, {})))
        return pipeline

    factories = {
        'make_doc': create_tokenizer,
        'tensorizer': lambda nlp, **cfg: [TokenVectorEncoder(nlp.vocab, **cfg)],
        'tagger': lambda nlp, **cfg: [NeuralTagger(nlp.vocab, **cfg)],
        'parser': lambda nlp, **cfg: [
            NeuralDependencyParser(nlp.vocab, **cfg),
            nonproj.deprojectivize],
        'ner': lambda nlp, **cfg: [NeuralEntityRecognizer(nlp.vocab, **cfg)],
        'similarity': lambda nlp, **cfg: [SimilarityHook(nlp.vocab, **cfg)],
        'textcat': lambda nlp, **cfg: [TextCategorizer(nlp.vocab, **cfg)],
        # Temporary compatibility -- delete after pivot
        'token_vectors': lambda nlp, **cfg: [TokenVectorEncoder(nlp.vocab, **cfg)],
        'tags': lambda nlp, **cfg: [NeuralTagger(nlp.vocab, **cfg)],
        'dependencies': lambda nlp, **cfg: [
            NeuralDependencyParser(nlp.vocab, **cfg),
            nonproj.deprojectivize,
        ],
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
    syntax_iterators = {}


class Language(object):
    """A text-processing pipeline. Usually you'll load this once per process,
    and pass the instance around your application.

    Defaults (class): Settings, data and factory methods for creating the `nlp`
        object and processing pipeline.
    lang (unicode): Two-letter language ID, i.e. ISO code.
    """
    Defaults = BaseDefaults
    lang = None

    def __init__(self, vocab=True, make_doc=True, pipeline=None,
                 meta={}, disable=tuple(), **kwargs):
        """Initialise a Language object.

        vocab (Vocab): A `Vocab` object. If `True`, a vocab is created via
            `Language.Defaults.create_vocab`.
        make_doc (callable): A function that takes text and returns a `Doc`
            object. Usually a `Tokenizer`.
        pipeline (list): A list of annotation processes or IDs of annotation,
            processes, e.g. a `Tagger` object, or `'tagger'`. IDs are looked
            up in `Language.Defaults.factories`.
        disable (list): A list of component names to exclude from the pipeline.
            The disable list has priority over the pipeline list -- if the same
            string occurs in both, the component is not loaded.
        meta (dict): Custom meta data for the Language class. Is written to by
            models to add model meta data.
        RETURNS (Language): The newly constructed object.
        """
        self._meta = dict(meta)
        if vocab is True:
            factory = self.Defaults.create_vocab
            vocab = factory(self, **meta.get('vocab', {}))
        self.vocab = vocab
        if make_doc is True:
            factory = self.Defaults.create_tokenizer
            make_doc = factory(self, **meta.get('tokenizer', {}))
        self.tokenizer = make_doc
        if pipeline is True:
            self.pipeline = self.Defaults.create_pipeline(self, disable)
        elif pipeline:
            # Careful not to do getattr(p, 'name', None) here
            # If we had disable=[None], we'd disable everything!
            self.pipeline = [p for p in pipeline
                             if p not in disable
                             and getattr(p, 'name', p) not in disable]
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

    @property
    def meta(self):
        self._meta.setdefault('lang', self.vocab.lang)
        self._meta.setdefault('name', '')
        self._meta.setdefault('version', '0.0.0')
        self._meta.setdefault('spacy_version', about.__version__)
        self._meta.setdefault('description', '')
        self._meta.setdefault('author', '')
        self._meta.setdefault('email', '')
        self._meta.setdefault('url', '')
        self._meta.setdefault('license', '')
        pipeline = []
        for component in self.pipeline:
            if hasattr(component, 'name'):
                pipeline.append(component.name)
        self._meta['pipeline'] = pipeline
        return self._meta

    @meta.setter
    def meta(self, value):
        self._meta = value

    # Conveniences to access pipeline components
    @property
    def tensorizer(self):
        return self.get_component('tensorizer')

    @property
    def tagger(self):
        return self.get_component('tagger')

    @property
    def parser(self):
        return self.get_component('parser')

    @property
    def entity(self):
        return self.get_component('ner')

    @property
    def matcher(self):
        return self.get_component('matcher')

    def get_component(self, name): 
        if self.pipeline in (True, None):
            return None
        for proc in self.pipeline:
            if hasattr(proc, 'name') and proc.name.endswith(name):
                return proc
        return None

    def __call__(self, text, disable=[]):
        """'Apply the pipeline to some text. The text can span multiple sentences,
        and can contain arbtrary whitespace. Alignment into the original string
        is preserved.

        text (unicode): The text to be processed.
        disable (list): Names of the pipeline components to disable.
        RETURNS (Doc): A container for accessing the annotations.

        EXAMPLE:
            >>> tokens = nlp('An example sentence. Another example sentence.')
            >>> tokens[0].text, tokens[0].head.tag_
            ('An', 'NN')
        """
        doc = self.make_doc(text)
        for proc in self.pipeline:
            name = getattr(proc, 'name', None)
            if name in disable:
                continue
            doc = proc(doc)
        return doc

    def make_doc(self, text):
        return self.tokenizer(text)

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
        grads = {}
        def get_grads(W, dW, key=None):
            grads[key] = (W, dW)
        pipes = list(self.pipeline[1:])
        random.shuffle(pipes)
        for proc in pipes:
            if not hasattr(proc, 'update'):
                continue
            tokvecses, bp_tokvecses = tok2vec.model.begin_update(feats, drop=drop)
            d_tokvecses = proc.update((docs, tokvecses), golds,
                                      drop=drop, sgd=get_grads, losses=losses)
            if d_tokvecses is not None:
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
        if self.parser:
            self.pipeline.append(NeuralLabeller(self.vocab))
        # Populate vocab
        for _, annots_brackets in get_gold_tuples():
            for annots, _ in annots_brackets:
                for word in annots[1]:
                    _ = self.vocab[word]
        contexts = []
        if cfg.get('device', -1) >= 0:
            import cupy.cuda.device
            device = cupy.cuda.device.Device(cfg['device'])
            device.use()
            Model.ops = CupyOps()
            Model.Ops = CupyOps
        else:
            device = None
        for proc in self.pipeline:
            if hasattr(proc, 'begin_training'):
                context = proc.begin_training(get_gold_tuples(),
                                              pipeline=self.pipeline)
                contexts.append(context)
        learn_rate = util.env_opt('learn_rate', 0.001)
        beta1 = util.env_opt('optimizer_B1', 0.9)
        beta2 = util.env_opt('optimizer_B2', 0.999)
        eps = util.env_opt('optimizer_eps', 1e-08)
        L2 = util.env_opt('L2_penalty', 1e-6)
        max_grad_norm = util.env_opt('grad_norm_clip', 1.)
        optimizer = Adam(Model.ops, learn_rate, L2=L2, beta1=beta1,
                         beta2=beta2, eps=eps)
        optimizer.max_grad_norm = max_grad_norm
        optimizer.device = device
        return optimizer

    def evaluate(self, docs_golds):
        docs, golds = zip(*docs_golds)
        scorer = Scorer()
        for doc, gold in zip(self.pipe(docs, batch_size=32), golds):
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

    def pipe(self, texts, n_threads=2, batch_size=1000, disable=[]):
        """Process texts as a stream, and yield `Doc` objects in order. Supports
        GIL-free multi-threading.

        texts (iterator): A sequence of texts to process.
        n_threads (int): The number of worker threads to use. If -1, OpenMP will
            decide how many to use at run time. Default is 2.
        batch_size (int): The number of texts to buffer.
        disable (list): Names of the pipeline components to disable.
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
            if name in disable:
                continue
            if hasattr(proc, 'pipe'):
                docs = proc.pipe(docs, n_threads=n_threads, batch_size=batch_size)
            else:
                # Apply the function, but yield the doc
                docs = _pipe(proc, docs)
        for doc in docs:
            yield doc

    def to_disk(self, path, disable=tuple()):
        """Save the current state to a directory.  If a model is loaded, this
        will include the model.

        path (unicode or Path): A path to a directory, which will be created if
            it doesn't exist. Paths may be either strings or `Path`-like objects.
        disable (list): Names of pipeline components to disable and prevent
            from being saved.

        EXAMPLE:
            >>> nlp.to_disk('/path/to/models')
        """
        path = util.ensure_path(path)
        serializers = OrderedDict((
            ('vocab', lambda p: self.vocab.to_disk(p)),
            ('tokenizer', lambda p: self.tokenizer.to_disk(p, vocab=False)),
            ('meta.json', lambda p: p.open('w').write(json_dumps(self.meta)))
        ))
        for proc in self.pipeline:
            if not hasattr(proc, 'name'):
                continue
            if proc.name in disable:
                continue
            if not hasattr(proc, 'to_disk'):
                continue
            serializers[proc.name] = lambda p, proc=proc: proc.to_disk(p, vocab=False)
        util.to_disk(path, serializers, {p: False for p in disable})

    def from_disk(self, path, disable=tuple()):
        """Loads state from a directory. Modifies the object in place and
        returns it. If the saved `Language` object contains a model, the
        model will be loaded.

        path (unicode or Path): A path to a directory. Paths may be either
            strings or `Path`-like objects.
        disable (list): Names of the pipeline components to disable.
        RETURNS (Language): The modified `Language` object.

        EXAMPLE:
            >>> from spacy.language import Language
            >>> nlp = Language().from_disk('/path/to/models')
        """
        path = util.ensure_path(path)
        deserializers = OrderedDict((
            ('vocab', lambda p: self.vocab.from_disk(p)),
            ('tokenizer', lambda p: self.tokenizer.from_disk(p, vocab=False)),
            ('meta.json', lambda p: p.open('w').write(json_dumps(self.meta)))
        ))
        for proc in self.pipeline:
            if not hasattr(proc, 'name'):
                continue
            if proc.name in disable:
                continue
            if not hasattr(proc, 'to_disk'):
                continue
            deserializers[proc.name] = lambda p, proc=proc: proc.from_disk(p, vocab=False)
        exclude = {p: False for p in disable}
        if not (path / 'vocab').exists():
            exclude['vocab'] = True
        util.from_disk(path, deserializers, exclude)
        return self

    def to_bytes(self, disable=[]):
        """Serialize the current state to a binary string.

        disable (list): Nameds of pipeline components to disable and prevent
            from being serialized.
        RETURNS (bytes): The serialized form of the `Language` object.
        """
        serializers = OrderedDict((
            ('vocab', lambda: self.vocab.to_bytes()),
            ('tokenizer', lambda: self.tokenizer.to_bytes(vocab=False)),
            ('meta', lambda: ujson.dumps(self.meta))
        ))
        for i, proc in enumerate(self.pipeline):
            if getattr(proc, 'name', None) in disable:
                continue
            if not hasattr(proc, 'to_bytes'):
                continue
            serializers[i] = lambda proc=proc: proc.to_bytes(vocab=False)
        return util.to_bytes(serializers, {})

    def from_bytes(self, bytes_data, disable=[]):
        """Load state from a binary string.

        bytes_data (bytes): The data to load from.
        disable (list): Names of the pipeline components to disable.
        RETURNS (Language): The `Language` object.
        """
        deserializers = OrderedDict((
            ('vocab', lambda b: self.vocab.from_bytes(b)),
            ('tokenizer', lambda b: self.tokenizer.from_bytes(b, vocab=False)),
            ('meta', lambda b: self.meta.update(ujson.loads(b)))
        ))
        for i, proc in enumerate(self.pipeline):
            if getattr(proc, 'name', None) in disable:
                continue
            if not hasattr(proc, 'from_bytes'):
                continue
            deserializers[i] = lambda b, proc=proc: proc.from_bytes(b, vocab=False)
        msg = util.from_bytes(bytes_data, deserializers, {})
        return self


def _pipe(func, docs):
    for doc in docs:
        func(doc)
        yield doc
