# coding: utf8
from __future__ import absolute_import, unicode_literals

import random
import ujson
import itertools
import weakref
import functools
from collections import OrderedDict
from contextlib import contextmanager
from copy import copy
from thinc.neural import Model
from thinc.neural.optimizers import Adam

from .tokenizer import Tokenizer
from .vocab import Vocab
from .lemmatizer import Lemmatizer
from .pipeline import DependencyParser, Tensorizer, Tagger, EntityRecognizer
from .pipeline import SimilarityHook, TextCategorizer, SentenceSegmenter
from .pipeline import merge_noun_chunks, merge_entities
from .compat import json_dumps, izip, basestring_
from .gold import GoldParse
from .scorer import Scorer
from ._ml import link_vectors_to_models, create_default_optimizer
from .attrs import IS_STOP
from .lang.punctuation import TOKENIZER_PREFIXES, TOKENIZER_SUFFIXES
from .lang.punctuation import TOKENIZER_INFIXES
from .lang.tokenizer_exceptions import TOKEN_MATCH
from .lang.tag_map import TAG_MAP
from .lang.lex_attrs import LEX_ATTRS, is_stop
from .errors import Errors
from . import util
from . import about


class BaseDefaults(object):
    @classmethod
    def create_lemmatizer(cls, nlp=None):
        return Lemmatizer(cls.lemma_index, cls.lemma_exc, cls.lemma_rules,
                          cls.lemma_lookup)

    @classmethod
    def create_vocab(cls, nlp=None):
        lemmatizer = cls.create_lemmatizer(nlp)
        lex_attr_getters = dict(cls.lex_attr_getters)
        # This is messy, but it's the minimal working fix to Issue #639.
        lex_attr_getters[IS_STOP] = functools.partial(is_stop,
                                                      stops=cls.stop_words)
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
        prefix_search = (util.compile_prefix_regex(cls.prefixes).search
                         if cls.prefixes else None)
        suffix_search = (util.compile_suffix_regex(cls.suffixes).search
                         if cls.suffixes else None)
        infix_finditer = (util.compile_infix_regex(cls.infixes).finditer
                          if cls.infixes else None)
        vocab = nlp.vocab if nlp is not None else cls.create_vocab(nlp)
        return Tokenizer(vocab, rules=rules,
                         prefix_search=prefix_search,
                         suffix_search=suffix_search,
                         infix_finditer=infix_finditer,
                         token_match=token_match)

    pipe_names = ['tagger', 'parser', 'ner']
    token_match = TOKEN_MATCH
    prefixes = tuple(TOKENIZER_PREFIXES)
    suffixes = tuple(TOKENIZER_SUFFIXES)
    infixes = tuple(TOKENIZER_INFIXES)
    tag_map = dict(TAG_MAP)
    tokenizer_exceptions = {}
    stop_words = set()
    lemma_rules = {}
    lemma_exc = {}
    lemma_index = {}
    lemma_lookup = {}
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

    factories = {
        'tokenizer': lambda nlp: nlp.Defaults.create_tokenizer(nlp),
        'tensorizer': lambda nlp, **cfg: Tensorizer(nlp.vocab, **cfg),
        'tagger': lambda nlp, **cfg: Tagger(nlp.vocab, **cfg),
        'parser': lambda nlp, **cfg: DependencyParser(nlp.vocab, **cfg),
        'ner': lambda nlp, **cfg: EntityRecognizer(nlp.vocab, **cfg),
        'similarity': lambda nlp, **cfg: SimilarityHook(nlp.vocab, **cfg),
        'textcat': lambda nlp, **cfg: TextCategorizer(nlp.vocab, **cfg),
        'sbd': lambda nlp, **cfg: SentenceSegmenter(nlp.vocab, **cfg),
        'sentencizer': lambda nlp, **cfg: SentenceSegmenter(nlp.vocab, **cfg),
        'merge_noun_chunks': lambda nlp, **cfg: merge_noun_chunks,
        'merge_entities': lambda nlp, **cfg: merge_entities
    }

    def __init__(self, vocab=True, make_doc=True, max_length=10**6, meta={}, **kwargs):
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
        max_length (int) :
            Maximum number of characters in a single text. The current v2 models
            may run out memory on extremely long texts, due to large internal
            allocations. You should segment these texts into meaningful units,
            e.g. paragraphs, subsections etc, before passing them to spaCy.
            Default maximum length is 1,000,000 characters (1mb). As a rule of
            thumb, if all pipeline components are enabled, spaCy's default
            models currently requires roughly 1GB of temporary memory per
            100,000 characters in one text.
        RETURNS (Language): The newly constructed object.
        """
        self._meta = dict(meta)
        self._path = None
        if vocab is True:
            factory = self.Defaults.create_vocab
            vocab = factory(self, **meta.get('vocab', {}))
            if vocab.vectors.name is None:
                vocab.vectors.name = meta.get('vectors', {}).get('name')
        self.vocab = vocab
        if make_doc is True:
            factory = self.Defaults.create_tokenizer
            make_doc = factory(self, **meta.get('tokenizer', {}))
        self.tokenizer = make_doc
        self.pipeline = []
        self.max_length = max_length
        self._optimizer = None

    @property
    def path(self):
        return self._path

    @property
    def meta(self):
        self._meta.setdefault('lang', self.vocab.lang)
        self._meta.setdefault('name', 'model')
        self._meta.setdefault('version', '0.0.0')
        self._meta.setdefault('spacy_version', '>={}'.format(about.__version__))
        self._meta.setdefault('description', '')
        self._meta.setdefault('author', '')
        self._meta.setdefault('email', '')
        self._meta.setdefault('url', '')
        self._meta.setdefault('license', '')
        self._meta['vectors'] = {'width': self.vocab.vectors_length,
                                 'vectors': len(self.vocab.vectors),
                                 'keys': self.vocab.vectors.n_keys,
                                 'name': self.vocab.vectors.name}
        self._meta['pipeline'] = self.pipe_names
        return self._meta

    @meta.setter
    def meta(self, value):
        self._meta = value

    # Conveniences to access pipeline components
    @property
    def tensorizer(self):
        return self.get_pipe('tensorizer')

    @property
    def tagger(self):
        return self.get_pipe('tagger')

    @property
    def parser(self):
        return self.get_pipe('parser')

    @property
    def entity(self):
        return self.get_pipe('ner')

    @property
    def matcher(self):
        return self.get_pipe('matcher')

    @property
    def pipe_names(self):
        """Get names of available pipeline components.

        RETURNS (list): List of component name strings, in order.
        """
        return [pipe_name for pipe_name, _ in self.pipeline]

    def get_pipe(self, name):
        """Get a pipeline component for a given component name.

        name (unicode): Name of pipeline component to get.
        RETURNS (callable): The pipeline component.
        """
        for pipe_name, component in self.pipeline:
            if pipe_name == name:
                return component
        raise KeyError(Errors.E001.format(name=name, opts=self.pipe_names))

    def create_pipe(self, name, config=dict()):
        """Create a pipeline component from a factory.

        name (unicode): Factory name to look up in `Language.factories`.
        config (dict): Configuration parameters to initialise component.
        RETURNS (callable): Pipeline component.
        """
        if name not in self.factories:
            raise KeyError(Errors.E002.format(name=name))
        factory = self.factories[name]
        return factory(self, **config)

    def add_pipe(self, component, name=None, before=None, after=None,
                 first=None, last=None):
        """Add a component to the processing pipeline. Valid components are
        callables that take a `Doc` object, modify it and return it. Only one
        of before/after/first/last can be set. Default behaviour is "last".

        component (callable): The pipeline component.
        name (unicode): Name of pipeline component. Overwrites existing
            component.name attribute if available. If no name is set and
            the component exposes no name attribute, component.__name__ is
            used. An error is raised if a name already exists in the pipeline.
        before (unicode): Component name to insert component directly before.
        after (unicode): Component name to insert component directly after.
        first (bool): Insert component first / not first in the pipeline.
        last (bool): Insert component last / not last in the pipeline.

        EXAMPLE:
            >>> nlp.add_pipe(component, before='ner')
            >>> nlp.add_pipe(component, name='custom_name', last=True)
        """
        if not hasattr(component, '__call__'):
            msg = Errors.E003.format(component=repr(component), name=name)
            if isinstance(component, basestring_) and component in self.factories:
                msg += Errors.E004.format(component=component)
            raise ValueError(msg)
        if name is None:
            if hasattr(component, 'name'):
                name = component.name
            elif hasattr(component, '__name__'):
                name = component.__name__
            elif (hasattr(component, '__class__') and
                  hasattr(component.__class__, '__name__')):
                name = component.__class__.__name__
            else:
                name = repr(component)
        if name in self.pipe_names:
            raise ValueError(Errors.E007.format(name=name, opts=self.pipe_names))
        if sum([bool(before), bool(after), bool(first), bool(last)]) >= 2:
            raise ValueError(Errors.E006)
        pipe = (name, component)
        if last or not any([first, before, after]):
            self.pipeline.append(pipe)
        elif first:
            self.pipeline.insert(0, pipe)
        elif before and before in self.pipe_names:
            self.pipeline.insert(self.pipe_names.index(before), pipe)
        elif after and after in self.pipe_names:
            self.pipeline.insert(self.pipe_names.index(after) + 1, pipe)
        else:
            raise ValueError(Errors.E001.format(name=before or after,
                                                opts=self.pipe_names))

    def has_pipe(self, name):
        """Check if a component name is present in the pipeline. Equivalent to
        `name in nlp.pipe_names`.

        name (unicode): Name of the component.
        RETURNS (bool): Whether a component of the name exists in the pipeline.
        """
        return name in self.pipe_names

    def replace_pipe(self, name, component):
        """Replace a component in the pipeline.

        name (unicode): Name of the component to replace.
        component (callable): Pipeline component.
        """
        if name not in self.pipe_names:
            raise ValueError(Errors.E001.format(name=name, opts=self.pipe_names))
        self.pipeline[self.pipe_names.index(name)] = (name, component)

    def rename_pipe(self, old_name, new_name):
        """Rename a pipeline component.

        old_name (unicode): Name of the component to rename.
        new_name (unicode): New name of the component.
        """
        if old_name not in self.pipe_names:
            raise ValueError(Errors.E001.format(name=old_name, opts=self.pipe_names))
        if new_name in self.pipe_names:
            raise ValueError(Errors.E007.format(name=new_name, opts=self.pipe_names))
        i = self.pipe_names.index(old_name)
        self.pipeline[i] = (new_name, self.pipeline[i][1])

    def remove_pipe(self, name):
        """Remove a component from the pipeline.

        name (unicode): Name of the component to remove.
        RETURNS (tuple): A `(name, component)` tuple of the removed component.
        """
        if name not in self.pipe_names:
            raise ValueError(Errors.E001.format(name=name, opts=self.pipe_names))
        return self.pipeline.pop(self.pipe_names.index(name))

    def __call__(self, text, disable=[]):
        """Apply the pipeline to some text. The text can span multiple sentences,
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
        if len(text) >= self.max_length:
            raise ValueError(Errors.E088.format(length=len(text),
                                                max_length=self.max_length))
        doc = self.make_doc(text)
        for name, proc in self.pipeline:
            if name in disable:
                continue
            if not hasattr(proc, '__call__'):
                raise ValueError(Errors.E003.format(component=type(proc), name=name))
            doc = proc(doc)
            if doc is None:
                raise ValueError(Errors.E005.format(name=name))
        return doc

    def disable_pipes(self, *names):
        """Disable one or more pipeline components. If used as a context
        manager, the pipeline will be restored to the initial state at the end
        of the block. Otherwise, a DisabledPipes object is returned, that has
        a `.restore()` method you can use to undo your changes.

        EXAMPLE:
            >>> nlp.add_pipe('parser')
            >>> nlp.add_pipe('tagger')
            >>> with nlp.disable_pipes('parser', 'tagger'):
            >>>     assert not nlp.has_pipe('parser')
            >>> assert nlp.has_pipe('parser')
            >>> disabled = nlp.disable_pipes('parser')
            >>> assert len(disabled) == 1
            >>> assert not nlp.has_pipe('parser')
            >>> disabled.restore()
            >>> assert nlp.has_pipe('parser')
        """
        return DisabledPipes(self, *names)

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
            >>> with nlp.begin_training(gold) as (trainer, optimizer):
            >>>    for epoch in trainer.epochs(gold):
            >>>        for docs, golds in epoch:
            >>>            state = nlp.update(docs, golds, sgd=optimizer)
        """
        if len(docs) != len(golds):
            raise IndexError(Errors.E009.format(n_docs=len(docs), n_golds=len(golds)))
        if len(docs) == 0:
            return
        if sgd is None:
            if self._optimizer is None:
                self._optimizer = create_default_optimizer(Model.ops)
            sgd = self._optimizer

        # Allow dict of args to GoldParse, instead of GoldParse objects.
        gold_objs = []
        doc_objs = []
        for doc, gold in zip(docs, golds):
            if isinstance(doc, basestring_):
                doc = self.make_doc(doc)
            if not isinstance(gold, GoldParse):
                gold = GoldParse(doc, **gold)
            doc_objs.append(doc)
            gold_objs.append(gold)
        golds = gold_objs
        docs = doc_objs
        grads = {}

        def get_grads(W, dW, key=None):
            grads[key] = (W, dW)

        pipes = list(self.pipeline)
        random.shuffle(pipes)
        for name, proc in pipes:
            if not hasattr(proc, 'update'):
                continue
            grads = {}
            proc.update(docs, golds, drop=drop, sgd=get_grads, losses=losses)
            for key, (W, dW) in grads.items():
                sgd(W, dW, key=key)

    def preprocess_gold(self, docs_golds):
        """Can be called before training to pre-process gold data. By default,
        it handles nonprojectivity and adds missing tags to the tag map.

        docs_golds (iterable): Tuples of `Doc` and `GoldParse` objects.
        YIELDS (tuple): Tuples of preprocessed `Doc` and `GoldParse` objects.
        """
        for name, proc in self.pipeline:
            if hasattr(proc, 'preprocess_gold'):
                docs_golds = proc.preprocess_gold(docs_golds)
        for doc, gold in docs_golds:
            yield doc, gold

    def begin_training(self, get_gold_tuples=None, sgd=None, **cfg):
        """Allocate models, pre-process training data and acquire a trainer and
        optimizer. Used as a contextmanager.

        get_gold_tuples (function): Function returning gold data
        **cfg: Config parameters.
        RETURNS: An optimizer
        """
        if get_gold_tuples is None:
            get_gold_tuples = lambda: []
        # Populate vocab
        else:
            for _, annots_brackets in get_gold_tuples():
                for annots, _ in annots_brackets:
                    for word in annots[1]:
                        _ = self.vocab[word]
        contexts = []
        if cfg.get('device', -1) >= 0:
            device = util.use_gpu(cfg['device'])
            if self.vocab.vectors.data.shape[1] >= 1:
                self.vocab.vectors.data = Model.ops.asarray(
                    self.vocab.vectors.data)
        else:
            device = None
        link_vectors_to_models(self.vocab)
        if self.vocab.vectors.data.shape[1]:
            cfg['pretrained_vectors'] = self.vocab.vectors.name
        if sgd is None:
            sgd = create_default_optimizer(Model.ops)
        self._optimizer = sgd
        for name, proc in self.pipeline:
            if hasattr(proc, 'begin_training'):
                proc.begin_training(get_gold_tuples(),
                                    pipeline=self.pipeline,
                                    sgd=self._optimizer,
                                    **cfg)
        return self._optimizer

    def evaluate(self, docs_golds, verbose=False):
        scorer = Scorer()
        docs, golds = zip(*docs_golds)
        docs = list(docs)
        golds = list(golds)
        for name, pipe in self.pipeline:
            if not hasattr(pipe, 'pipe'):
                docs = (pipe(doc) for doc in docs)
            else:
                docs = pipe.pipe(docs, batch_size=256)
        for doc, gold in zip(docs, golds):
            if verbose:
                print(doc)
            scorer.score(doc, gold, verbose=verbose)
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
        contexts = [pipe.use_params(params) for name, pipe
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

    def pipe(self, texts, as_tuples=False, n_threads=2, batch_size=1000,
             disable=[], cleanup=False):
        """Process texts as a stream, and yield `Doc` objects in order.

        texts (iterator): A sequence of texts to process.
        as_tuples (bool):
            If set to True, inputs should be a sequence of
            (text, context) tuples. Output will then be a sequence of
            (doc, context) tuples. Defaults to False.
        n_threads (int): Currently inactive.
        batch_size (int): The number of texts to buffer.
        disable (list): Names of the pipeline components to disable.
        cleanup (bool): If True, unneeded strings are freed,
            to control memory use. Experimental.
        YIELDS (Doc): Documents in the order of the original text.

        EXAMPLE:
            >>> texts = [u'One document.', u'...', u'Lots of documents']
            >>>     for doc in nlp.pipe(texts, batch_size=50, n_threads=4):
            >>>         assert doc.is_parsed
        """
        if as_tuples:
            text_context1, text_context2 = itertools.tee(texts)
            texts = (tc[0] for tc in text_context1)
            contexts = (tc[1] for tc in text_context2)
            docs = self.pipe(texts, n_threads=n_threads, batch_size=batch_size,
                             disable=disable)
            for doc, context in izip(docs, contexts):
                yield (doc, context)
            return
        docs = (self.make_doc(text) for text in texts)
        for name, proc in self.pipeline:
            if name in disable:
                continue
            if hasattr(proc, 'pipe'):
                docs = proc.pipe(docs, n_threads=n_threads,
                                 batch_size=batch_size)
            else:
                # Apply the function, but yield the doc
                docs = _pipe(proc, docs)
        # Track weakrefs of "recent" documents, so that we can see when they
        # expire from memory. When they do, we know we don't need old strings.
        # This way, we avoid maintaining an unbounded growth in string entries
        # in the string store.
        recent_refs = weakref.WeakSet()
        old_refs = weakref.WeakSet()
        # Keep track of the original string data, so that if we flush old strings,
        # we can recover the original ones. However, we only want to do this if we're
        # really adding strings, to save up-front costs.
        original_strings_data = None
        nr_seen = 0
        for doc in docs:
            yield doc
            if cleanup:
                recent_refs.add(doc)
                if nr_seen < 10000:
                    old_refs.add(doc)
                    nr_seen += 1
                elif len(old_refs) == 0:
                    old_refs, recent_refs = recent_refs, old_refs
                    if original_strings_data is None:
                        original_strings_data = list(self.vocab.strings)
                    else:
                        keys, strings = self.vocab.strings._cleanup_stale_strings(original_strings_data)
                        self.vocab._reset_cache(keys, strings)
                        self.tokenizer._reset_cache(keys)
                    nr_seen = 0

    def to_disk(self, path, disable=tuple()):
        """Save the current state to a directory.  If a model is loaded, this
        will include the model.

        path (unicode or Path): A path to a directory, which will be created if
            it doesn't exist. Paths may be strings or `Path`-like objects.
        disable (list): Names of pipeline components to disable and prevent
            from being saved.

        EXAMPLE:
            >>> nlp.to_disk('/path/to/models')
        """
        path = util.ensure_path(path)
        serializers = OrderedDict((
            ('tokenizer', lambda p: self.tokenizer.to_disk(p, vocab=False)),
            ('meta.json', lambda p: p.open('w').write(json_dumps(self.meta)))
        ))
        for name, proc in self.pipeline:
            if not hasattr(proc, 'name'):
                continue
            if name in disable:
                continue
            if not hasattr(proc, 'to_disk'):
                continue
            serializers[name] = lambda p, proc=proc: proc.to_disk(p, vocab=False)
        serializers['vocab'] = lambda p: self.vocab.to_disk(p)
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
            ('meta.json', lambda p: self.meta.update(util.read_json(p))),
            ('vocab', lambda p: (
                self.vocab.from_disk(p) and _fix_pretrained_vectors_name(self))),
            ('tokenizer', lambda p: self.tokenizer.from_disk(p, vocab=False)),
        ))
        for name, proc in self.pipeline:
            if name in disable:
                continue
            if not hasattr(proc, 'to_disk'):
                continue
            deserializers[name] = lambda p, proc=proc: proc.from_disk(p, vocab=False)
        exclude = {p: False for p in disable}
        if not (path / 'vocab').exists():
            exclude['vocab'] = True
        util.from_disk(path, deserializers, exclude)
        self._path = path
        return self

    def to_bytes(self, disable=[], **exclude):
        """Serialize the current state to a binary string.

        disable (list): Nameds of pipeline components to disable and prevent
            from being serialized.
        RETURNS (bytes): The serialized form of the `Language` object.
        """
        serializers = OrderedDict((
            ('vocab', lambda: self.vocab.to_bytes()),
            ('tokenizer', lambda: self.tokenizer.to_bytes(vocab=False)),
            ('meta', lambda: json_dumps(self.meta))
        ))
        for i, (name, proc) in enumerate(self.pipeline):
            if name in disable:
                continue
            if not hasattr(proc, 'to_bytes'):
                continue
            serializers[i] = lambda proc=proc: proc.to_bytes(vocab=False)
        return util.to_bytes(serializers, exclude)

    def from_bytes(self, bytes_data, disable=[]):
        """Load state from a binary string.

        bytes_data (bytes): The data to load from.
        disable (list): Names of the pipeline components to disable.
        RETURNS (Language): The `Language` object.
        """
        deserializers = OrderedDict((
            ('meta', lambda b: self.meta.update(ujson.loads(b))),
            ('vocab', lambda b: (
                self.vocab.from_bytes(b) and _fix_pretrained_vectors_name(self))),
            ('tokenizer', lambda b: self.tokenizer.from_bytes(b, vocab=False)),
        ))
        for i, (name, proc) in enumerate(self.pipeline):
            if name in disable:
                continue
            if not hasattr(proc, 'from_bytes'):
                continue
            deserializers[i] = lambda b, proc=proc: proc.from_bytes(b, vocab=False)
        msg = util.from_bytes(bytes_data, deserializers, {})
        return self


def _fix_pretrained_vectors_name(nlp):
    # TODO: Replace this once we handle vectors consistently as static
    # data
    if 'vectors' in nlp.meta and nlp.meta['vectors'].get('name'):
        nlp.vocab.vectors.name = nlp.meta['vectors']['name']
    elif not nlp.vocab.vectors.size:
        nlp.vocab.vectors.name = None
    elif 'name' in nlp.meta and 'lang' in nlp.meta:
        vectors_name = '%s_%s.vectors' % (nlp.meta['lang'], nlp.meta['name'])
        nlp.vocab.vectors.name = vectors_name
    else:
        raise ValueError(Errors.E092)
    if nlp.vocab.vectors.size != 0:
        link_vectors_to_models(nlp.vocab)
    for name, proc in nlp.pipeline:
        if not hasattr(proc, 'cfg'):
            continue
        proc.cfg.setdefault('deprecation_fixes', {})
        proc.cfg['deprecation_fixes']['vectors_name'] = nlp.vocab.vectors.name


class DisabledPipes(list):
    """Manager for temporary pipeline disabling."""
    def __init__(self, nlp, *names):
        self.nlp = nlp
        self.names = names
        # Important! Not deep copy -- we just want the container (but we also
        # want to support people providing arbitrarily typed nlp.pipeline
        # objects.)
        self.original_pipeline = copy(nlp.pipeline)
        list.__init__(self)
        self.extend(nlp.remove_pipe(name) for name in names)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.restore()

    def restore(self):
        '''Restore the pipeline to its state when DisabledPipes was created.'''
        current, self.nlp.pipeline = self.nlp.pipeline, self.original_pipeline
        unexpected = [name for name, pipe in current
                      if not self.nlp.has_pipe(name)]
        if unexpected:
            # Don't change the pipeline if we're raising an error.
            self.nlp.pipeline = current
            raise ValueError(Errors.E008.format(names=unexpected))
        self[:] = []


def _pipe(func, docs):
    for doc in docs:
        doc = func(doc)
        yield doc
