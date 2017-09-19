# cython: infer_types=True
# cython: profile=True
# coding: utf8
from __future__ import unicode_literals

from thinc.api import chain, layerize, with_getitem
from thinc.neural import Model, Softmax
import numpy
cimport numpy as np
import cytoolz
import util
from collections import OrderedDict
import ujson
import msgpack

from thinc.api import add, layerize, chain, clone, concatenate, with_flatten
from thinc.neural import Model, Maxout, Softmax, Affine
from thinc.neural._classes.hash_embed import HashEmbed
from thinc.neural.util import to_categorical

from thinc.neural.pooling import Pooling, max_pool, mean_pool
from thinc.neural._classes.difference import Siamese, CauchySimilarity

from thinc.neural._classes.convolution import ExtractWindow
from thinc.neural._classes.resnet import Residual
from thinc.neural._classes.batchnorm import BatchNorm as BN

from .tokens.doc cimport Doc
from .syntax.parser cimport Parser as LinearParser
from .syntax.nn_parser cimport Parser as NeuralParser
from .syntax.parser import get_templates as get_feature_templates
from .syntax.beam_parser cimport BeamParser
from .syntax.ner cimport BiluoPushDown
from .syntax.arc_eager cimport ArcEager
from .tagger import Tagger
from .syntax.stateclass cimport StateClass
from .gold cimport GoldParse
from .morphology cimport Morphology
from .vocab cimport Vocab
from .syntax import nonproj
from .compat import json_dumps

from .attrs import ID, LOWER, PREFIX, SUFFIX, SHAPE, TAG, DEP, POS
from ._ml import rebatch, Tok2Vec, flatten
from ._ml import build_text_classifier, build_tagger_model
from .parts_of_speech import X


class SentenceSegmenter(object):
    '''A simple spaCy hook, to allow custom sentence boundary detection logic
    (that doesn't require the dependency parse).

    To change the sentence boundary detection strategy, pass a generator
    function `strategy` on initialization, or assign a new strategy to
    the .strategy attribute.

    Sentence detection strategies should be generators that take `Doc` objects
    and yield `Span` objects for each sentence.
    '''
    name = 'sbd'

    def __init__(self, vocab, strategy=None):
        self.vocab = vocab
        if strategy is None or strategy == 'on_punct':
            strategy = self.split_on_punct
        self.strategy = strategy

    def __call__(self, doc):
        doc.user_hooks['sents'] = self.strategy

    @staticmethod
    def split_on_punct(doc):
        start = 0
        seen_period = False
        for i, word in enumerate(doc):
            if seen_period and not word.is_punct:
                yield doc[start : word.i]
                start = word.i
                seen_period = False
            elif word.text in ['.', '!', '?']:
                seen_period = True
        if start < len(doc):
            yield doc[start : len(doc)]


class BaseThincComponent(object):
    name = None

    @classmethod
    def Model(cls, *shape, **kwargs):
        raise NotImplementedError

    def __init__(self, vocab, model=True, **cfg):
        raise NotImplementedError

    def __call__(self, doc):
        scores = self.predict([doc])
        self.set_annotations([doc], scores)
        return doc

    def pipe(self, stream, batch_size=128, n_threads=-1):
        for docs in cytoolz.partition_all(batch_size, stream):
            docs = list(docs)
            scores = self.predict(docs)
            self.set_annotations(docs, scores)
            yield from docs

    def predict(self, docs):
        raise NotImplementedError

    def set_annotations(self, docs, scores):
        raise NotImplementedError

    def update(self, docs_tensors, golds, state=None, drop=0., sgd=None, losses=None):
        raise NotImplementedError

    def get_loss(self, docs, golds, scores):
        raise NotImplementedError

    def begin_training(self, gold_tuples=tuple(), pipeline=None):
        token_vector_width = pipeline[0].model.nO
        if self.model is True:
            self.model = self.Model(1, token_vector_width)

    def use_params(self, params):
        with self.model.use_params(params):
            yield

    def to_bytes(self, **exclude):
        serialize = OrderedDict((
            ('cfg', lambda: json_dumps(self.cfg)),
            ('model', lambda: self.model.to_bytes()),
            ('vocab', lambda: self.vocab.to_bytes())
        ))
        return util.to_bytes(serialize, exclude)

    def from_bytes(self, bytes_data, **exclude):
        def load_model(b):
            if self.model is True:
                self.cfg['pretrained_dims'] = self.vocab.vectors_length
                self.model = self.Model(**self.cfg)
            self.model.from_bytes(b)

        deserialize = OrderedDict((
            ('cfg', lambda b: self.cfg.update(ujson.loads(b))),
            ('model', load_model),
            ('vocab', lambda b: self.vocab.from_bytes(b))
        ))
        util.from_bytes(bytes_data, deserialize, exclude)
        return self

    def to_disk(self, path, **exclude):
        serialize = OrderedDict((
            ('cfg', lambda p: p.open('w').write(json_dumps(self.cfg))),
            ('model', lambda p: p.open('wb').write(self.model.to_bytes())),
            ('vocab', lambda p: self.vocab.to_disk(p))
        ))
        util.to_disk(path, serialize, exclude)

    def from_disk(self, path, **exclude):
        def load_model(p):
            if self.model is True:
                self.cfg['pretrained_dims'] = self.vocab.vectors_length
                self.model = self.Model(**self.cfg)
            self.model.from_bytes(p.open('rb').read())

        deserialize = OrderedDict((
            ('cfg', lambda p: self.cfg.update(_load_cfg(p))),
            ('model', load_model),
            ('vocab', lambda p: self.vocab.from_disk(p)),
        ))
        util.from_disk(path, deserialize, exclude)
        return self


def _load_cfg(path):
    if path.exists():
        return ujson.load(path.open())
    else:
        return {}


class TokenVectorEncoder(BaseThincComponent):
    """Assign position-sensitive vectors to tokens, using a CNN or RNN."""
    name = 'tensorizer'

    @classmethod
    def Model(cls, width=128, embed_size=4000, **cfg):
        """Create a new statistical model for the class.

        width (int): Output size of the model.
        embed_size (int): Number of vectors in the embedding table.
        **cfg: Config parameters.
        RETURNS (Model): A `thinc.neural.Model` or similar instance.
        """
        width = util.env_opt('token_vector_width', width)
        embed_size = util.env_opt('embed_size', embed_size)
        return Tok2Vec(width, embed_size, **cfg)

    def __init__(self, vocab, model=True, **cfg):
        """Construct a new statistical model. Weights are not allocated on
        initialisation.

        vocab (Vocab): A `Vocab` instance. The model must share the same `Vocab`
            instance with the `Doc` objects it will process.
        model (Model): A `Model` instance or `True` allocate one later.
        **cfg: Config parameters.

        EXAMPLE:
            >>> from spacy.pipeline import TokenVectorEncoder
            >>> tok2vec = TokenVectorEncoder(nlp.vocab)
            >>> tok2vec.model = tok2vec.Model(128, 5000)
        """
        self.vocab = vocab
        self.model = model
        self.cfg = dict(cfg)
        self.cfg['pretrained_dims'] = self.vocab.vectors.data.shape[1]

    def __call__(self, doc):
        """Add context-sensitive vectors to a `Doc`, e.g. from a CNN or LSTM
        model. Vectors are set to the `Doc.tensor` attribute.

        docs (Doc or iterable): One or more documents to add vectors to.
        RETURNS (dict or None): Intermediate computations.
        """
        tokvecses = self.predict([doc])
        self.set_annotations([doc], tokvecses)
        return doc

    def pipe(self, stream, batch_size=128, n_threads=-1):
        """Process `Doc` objects as a stream.

        stream (iterator): A sequence of `Doc` objects to process.
        batch_size (int): Number of `Doc` objects to group.
        n_threads (int): Number of threads.
        YIELDS (iterator): A sequence of `Doc` objects, in order of input.
        """
        for docs in cytoolz.partition_all(batch_size, stream):
            docs = list(docs)
            tokvecses = self.predict(docs)
            self.set_annotations(docs, tokvecses)
            yield from docs

    def predict(self, docs):
        """Return a single tensor for a batch of documents.

        docs (iterable): A sequence of `Doc` objects.
        RETURNS (object): Vector representations for each token in the documents.
        """
        tokvecs = self.model(docs)
        return tokvecs

    def set_annotations(self, docs, tokvecses):
        """Set the tensor attribute for a batch of documents.

        docs (iterable): A sequence of `Doc` objects.
        tokvecs (object): Vector representation for each token in the documents.
        """
        for doc, tokvecs in zip(docs, tokvecses):
            assert tokvecs.shape[0] == len(doc)
            doc.tensor = tokvecs

    def update(self, docs, golds, state=None, drop=0., sgd=None, losses=None):
        """Update the model.

        docs (iterable): A batch of `Doc` objects.
        golds (iterable): A batch of `GoldParse` objects.
        drop (float): The droput rate.
        sgd (callable): An optimizer.
        RETURNS (dict): Results from the update.
        """
        if isinstance(docs, Doc):
            docs = [docs]
        tokvecs, bp_tokvecs = self.model.begin_update(docs, drop=drop)
        return tokvecs, bp_tokvecs

    def get_loss(self, docs, golds, scores):
        # TODO: implement
        raise NotImplementedError

    def begin_training(self, gold_tuples=tuple(), pipeline=None):
        """Allocate models, pre-process training data and acquire a trainer and
        optimizer.

        gold_tuples (iterable): Gold-standard training data.
        pipeline (list): The pipeline the model is part of.
        """
        if self.model is True:
            self.model = self.Model(
                pretrained_dims=self.vocab.vectors_length,
                **self.cfg)


class NeuralTagger(BaseThincComponent):
    name = 'tagger'
    def __init__(self, vocab, model=True, **cfg):
        self.vocab = vocab
        self.model = model
        self.cfg = dict(cfg)

    def __call__(self, doc):
        tags = self.predict(([doc], [doc.tensor]))
        self.set_annotations([doc], tags)
        return doc

    def pipe(self, stream, batch_size=128, n_threads=-1):
        for docs in cytoolz.partition_all(batch_size, stream):
            docs = list(docs)
            tokvecs = [d.tensor for d in docs]
            tag_ids = self.predict((docs, tokvecs))
            self.set_annotations(docs, tag_ids)
            yield from docs

    def predict(self, docs_tokvecs):
        scores = self.model(docs_tokvecs)
        scores = self.model.ops.flatten(scores)
        guesses = scores.argmax(axis=1)
        if not isinstance(guesses, numpy.ndarray):
            guesses = guesses.get()
        tokvecs = docs_tokvecs[1]
        guesses = self.model.ops.unflatten(guesses,
                    [tv.shape[0] for tv in tokvecs])
        return guesses

    def set_annotations(self, docs, batch_tag_ids):
        if isinstance(docs, Doc):
            docs = [docs]
        cdef Doc doc
        cdef int idx = 0
        cdef Vocab vocab = self.vocab
        for i, doc in enumerate(docs):
            doc_tag_ids = batch_tag_ids[i]
            if hasattr(doc_tag_ids, 'get'):
                doc_tag_ids = doc_tag_ids.get()
            for j, tag_id in enumerate(doc_tag_ids):
                # Don't clobber preset POS tags
                if doc.c[j].tag == 0 and doc.c[j].pos == 0:
                    vocab.morphology.assign_tag_id(&doc.c[j], tag_id)
                idx += 1
        doc.is_tagged = True

    def update(self, docs_tokvecs, golds, drop=0., sgd=None, losses=None):
        if losses is not None and self.name not in losses:
            losses[self.name] = 0.
        docs, tokvecs = docs_tokvecs

        if self.model.nI is None:
            self.model.nI = tokvecs[0].shape[1]
        tag_scores, bp_tag_scores = self.model.begin_update(docs_tokvecs, drop=drop)
        loss, d_tag_scores = self.get_loss(docs, golds, tag_scores)

        d_tokvecs = bp_tag_scores(d_tag_scores, sgd=sgd)
        if losses is not None:
            losses[self.name] += loss
        return d_tokvecs

    def get_loss(self, docs, golds, scores):
        scores = self.model.ops.flatten(scores)
        tag_index = {tag: i for i, tag in enumerate(self.vocab.morphology.tag_names)}

        cdef int idx = 0
        correct = numpy.zeros((scores.shape[0],), dtype='i')
        guesses = scores.argmax(axis=1)
        for gold in golds:
            for tag in gold.tags:
                if tag is None:
                    correct[idx] = guesses[idx]
                else:
                    correct[idx] = tag_index[tag]
                idx += 1
        correct = self.model.ops.xp.array(correct, dtype='i')
        d_scores = scores - to_categorical(correct, nb_classes=scores.shape[1])
        d_scores /= d_scores.shape[0]
        loss = (d_scores**2).sum()
        d_scores = self.model.ops.unflatten(d_scores, [len(d) for d in docs])
        return float(loss), d_scores

    def begin_training(self, gold_tuples=tuple(), pipeline=None):
        orig_tag_map = dict(self.vocab.morphology.tag_map)
        new_tag_map = {}
        for raw_text, annots_brackets in gold_tuples:
            for annots, brackets in annots_brackets:
                ids, words, tags, heads, deps, ents = annots
                for tag in tags:
                    if tag in orig_tag_map:
                        new_tag_map[tag] = orig_tag_map[tag]
                    else:
                        new_tag_map[tag] = {POS: X}
        if 'SP' not in new_tag_map:
            new_tag_map['SP'] = orig_tag_map.get('SP', {POS: X})
        cdef Vocab vocab = self.vocab
        if new_tag_map:
            vocab.morphology = Morphology(vocab.strings, new_tag_map,
                                          vocab.morphology.lemmatizer,
                                          exc=vocab.morphology.exc)
        token_vector_width = pipeline[0].model.nO
        if self.model is True:
            self.model = self.Model(self.vocab.morphology.n_tags, token_vector_width,
                                    pretrained_dims=self.vocab.vectors_length)

    @classmethod
    def Model(cls, n_tags, token_vector_width, pretrained_dims=0):
        return build_tagger_model(n_tags, token_vector_width,
                                  pretrained_dims)

    def use_params(self, params):
        with self.model.use_params(params):
            yield

    def to_bytes(self, **exclude):
        serialize = OrderedDict((
            ('model', lambda: self.model.to_bytes()),
            ('vocab', lambda: self.vocab.to_bytes()),
            ('tag_map', lambda: msgpack.dumps(self.vocab.morphology.tag_map,
                                             use_bin_type=True,
                                             encoding='utf8'))
        ))
        return util.to_bytes(serialize, exclude)

    def from_bytes(self, bytes_data, **exclude):
        def load_model(b):
            if self.model is True:
                token_vector_width = util.env_opt('token_vector_width',
                        self.cfg.get('token_vector_width', 128))
                self.model = self.Model(self.vocab.morphology.n_tags, token_vector_width,
                                        pretrained_dims=self.vocab.vectors_length)
            self.model.from_bytes(b)

        def load_tag_map(b):
            tag_map = msgpack.loads(b, encoding='utf8')
            self.vocab.morphology = Morphology(
                self.vocab.strings, tag_map=tag_map,
                lemmatizer=self.vocab.morphology.lemmatizer,
                exc=self.vocab.morphology.exc)

        deserialize = OrderedDict((
            ('vocab', lambda b: self.vocab.from_bytes(b)),
            ('tag_map', load_tag_map),
            ('model', lambda b: load_model(b)),
        ))
        util.from_bytes(bytes_data, deserialize, exclude)
        return self

    def to_disk(self, path, **exclude):
        serialize = OrderedDict((
            ('vocab', lambda p: self.vocab.to_disk(p)),
            ('tag_map', lambda p: p.open('wb').write(msgpack.dumps(
                self.vocab.morphology.tag_map,
                use_bin_type=True,
                encoding='utf8'))),
            ('model', lambda p: p.open('wb').write(self.model.to_bytes())),
            ('cfg', lambda p: p.open('w').write(json_dumps(self.cfg)))
        ))
        util.to_disk(path, serialize, exclude)

    def from_disk(self, path, **exclude):
        def load_model(p):
            if self.model is True:
                token_vector_width = util.env_opt('token_vector_width',
                        self.cfg.get('token_vector_width', 128))
                self.model = self.Model(self.vocab.morphology.n_tags, token_vector_width,
                                        **self.cfg)
            self.model.from_bytes(p.open('rb').read())

        def load_tag_map(p):
            with p.open('rb') as file_:
                tag_map = msgpack.loads(file_.read(), encoding='utf8')
            self.vocab.morphology = Morphology(
                self.vocab.strings, tag_map=tag_map,
                lemmatizer=self.vocab.morphology.lemmatizer,
                exc=self.vocab.morphology.exc)

        deserialize = OrderedDict((
            ('cfg', lambda p: self.cfg.update(_load_cfg(p))),
            ('vocab', lambda p: self.vocab.from_disk(p)),
            ('tag_map', load_tag_map),
            ('model', load_model),
        ))
        util.from_disk(path, deserialize, exclude)
        return self


class NeuralLabeller(NeuralTagger):
    name = 'nn_labeller'
    def __init__(self, vocab, model=True, **cfg):
        self.vocab = vocab
        self.model = model
        self.cfg = dict(cfg)

    @property
    def labels(self):
        return self.cfg.setdefault('labels', {})

    @labels.setter
    def labels(self, value):
        self.cfg['labels'] = value

    def set_annotations(self, docs, dep_ids):
        pass

    def begin_training(self, gold_tuples=tuple(), pipeline=None):
        gold_tuples = nonproj.preprocess_training_data(gold_tuples)
        for raw_text, annots_brackets in gold_tuples:
            for annots, brackets in annots_brackets:
                ids, words, tags, heads, deps, ents = annots
                for dep in deps:
                    if dep not in self.labels:
                        self.labels[dep] = len(self.labels)
        token_vector_width = pipeline[0].model.nO
        if self.model is True:
            self.model = self.Model(len(self.labels), token_vector_width,
                                    pretrained_dims=self.vocab.vectors_length)

    @classmethod
    def Model(cls, n_tags, token_vector_width, pretrained_dims=0):
        return build_tagger_model(n_tags, token_vector_width,
                                  pretrained_dims)

    def get_loss(self, docs, golds, scores):
        scores = self.model.ops.flatten(scores)
        cdef int idx = 0
        correct = numpy.zeros((scores.shape[0],), dtype='i')
        guesses = scores.argmax(axis=1)
        for gold in golds:
            for tag in gold.labels:
                if tag is None or tag not in self.labels:
                    correct[idx] = guesses[idx]
                else:
                    correct[idx] = self.labels[tag]
                idx += 1
        correct = self.model.ops.xp.array(correct, dtype='i')
        d_scores = scores - to_categorical(correct, nb_classes=scores.shape[1])
        d_scores /= d_scores.shape[0]
        loss = (d_scores**2).sum()
        d_scores = self.model.ops.unflatten(d_scores, [len(d) for d in docs])
        return float(loss), d_scores


class SimilarityHook(BaseThincComponent):
    """
    Experimental

    A pipeline component to install a hook for supervised similarity into
    Doc objects. Requires a Tensorizer to pre-process documents. The similarity
    model can be any object obeying the Thinc Model interface. By default,
    the model concatenates the elementwise mean and elementwise max of the two
    tensors, and compares them using the Cauchy-like similarity function
    from Chen (2013):

        similarity = 1. / (1. + (W * (vec1-vec2)**2).sum())

    Where W is a vector of dimension weights, initialized to 1.
    """
    name = 'similarity'
    def __init__(self, vocab, model=True, **cfg):
        self.vocab = vocab
        self.model = model
        self.cfg = dict(cfg)

    @classmethod
    def Model(cls, length):
        return Siamese(Pooling(max_pool, mean_pool), CauchySimilarity(length))

    def __call__(self, doc):
        '''Install similarity hook'''
        doc.user_hooks['similarity'] = self.predict
        return doc

    def pipe(self, docs, **kwargs):
        for doc in docs:
            yield self(doc)

    def predict(self, doc1, doc2):
        return self.model.predict([(doc1.tensor, doc2.tensor)])

    def update(self, doc1_tensor1_doc2_tensor2, golds, sgd=None, drop=0.):
        doc1s, tensor1s, doc2s, tensor2s = doc1_tensor1_doc2_tensor2
        sims, bp_sims = self.model.begin_update(zip(tensor1s, tensor2s),
                                                drop=drop)
        d_tensor1s, d_tensor2s = bp_sims(golds, sgd=sgd)

        return d_tensor1s, d_tensor2s

    def begin_training(self, _=tuple(), pipeline=None):
        """
        Allocate model, using width from tensorizer in pipeline.

        gold_tuples (iterable): Gold-standard training data.
        pipeline (list): The pipeline the model is part of.
        """
        if self.model is True:
            self.model = self.Model(pipeline[0].model.nO)


class TextCategorizer(BaseThincComponent):
    name = 'textcat'

    @classmethod
    def Model(cls, nr_class=1, width=64, **cfg):
        return build_text_classifier(nr_class, width, **cfg)

    def __init__(self, vocab, model=True, **cfg):
        self.vocab = vocab
        self.model = model
        self.cfg = dict(cfg)

    @property
    def labels(self):
        return self.cfg.get('labels', ['LABEL'])

    @labels.setter
    def labels(self, value):
        self.cfg['labels'] = value

    def __call__(self, doc):
        scores = self.predict([doc])
        self.set_annotations([doc], scores)
        return doc

    def pipe(self, stream, batch_size=128, n_threads=-1):
        for docs in cytoolz.partition_all(batch_size, stream):
            docs = list(docs)
            scores = self.predict(docs)
            self.set_annotations(docs, scores)
            yield from docs

    def predict(self, docs):
        scores = self.model(docs)
        scores = self.model.ops.asarray(scores)
        return scores

    def set_annotations(self, docs, scores):
        for i, doc in enumerate(docs):
            for j, label in enumerate(self.labels):
                doc.cats[label] = float(scores[i, j])

    def update(self, docs_tensors, golds, state=None, drop=0., sgd=None, losses=None):
        docs, tensors = docs_tensors
        scores, bp_scores = self.model.begin_update(docs, drop=drop)
        loss, d_scores = self.get_loss(docs, golds, scores)
        d_tensors = bp_scores(d_scores, sgd=sgd)
        if losses is not None:
            losses.setdefault(self.name, 0.0)
            losses[self.name] += loss
        return d_tensors

    def get_loss(self, docs, golds, scores):
        truths = numpy.zeros((len(golds), len(self.labels)), dtype='f')
        for i, gold in enumerate(golds):
            for j, label in enumerate(self.labels):
                truths[i, j] = label in gold.cats
        truths = self.model.ops.asarray(truths)
        d_scores = (scores-truths) / scores.shape[0]
        mean_square_error = ((scores-truths)**2).sum(axis=1).mean()
        return mean_square_error, d_scores

    def begin_training(self, gold_tuples=tuple(), pipeline=None):
        if pipeline and getattr(pipeline[0], 'name', None) == 'tensorizer':
            token_vector_width = pipeline[0].model.nO
        else:
            token_vector_width = 64
        if self.model is True:
            self.cfg['pretrained_dims'] = self.vocab.vectors_length
            self.model = self.Model(len(self.labels), token_vector_width,
                                    **self.cfg)


cdef class EntityRecognizer(LinearParser):
    """Annotate named entities on Doc objects."""
    TransitionSystem = BiluoPushDown

    feature_templates = get_feature_templates('ner')

    def add_label(self, label):
        LinearParser.add_label(self, label)
        if isinstance(label, basestring):
            label = self.vocab.strings[label]


cdef class BeamEntityRecognizer(BeamParser):
    """Annotate named entities on Doc objects."""
    TransitionSystem = BiluoPushDown

    feature_templates = get_feature_templates('ner')

    def add_label(self, label):
        LinearParser.add_label(self, label)
        if isinstance(label, basestring):
            label = self.vocab.strings[label]


cdef class DependencyParser(LinearParser):
    TransitionSystem = ArcEager
    feature_templates = get_feature_templates('basic')

    def add_label(self, label):
        LinearParser.add_label(self, label)
        if isinstance(label, basestring):
            label = self.vocab.strings[label]


cdef class NeuralDependencyParser(NeuralParser):
    name = 'parser'
    TransitionSystem = ArcEager

    def __reduce__(self):
        return (NeuralDependencyParser, (self.vocab, self.moves, self.model), None, None)


cdef class NeuralEntityRecognizer(NeuralParser):
    name = 'ner'
    TransitionSystem = BiluoPushDown

    nr_feature = 6

    def predict_confidences(self, docs):
        tensors = [d.tensor for d in docs]
        samples = []
        for i in range(10):
            states = self.parse_batch(docs, tensors, drop=0.3)
            for state in states:
                samples.append(self._get_entities(state))

    def __reduce__(self):
        return (NeuralEntityRecognizer, (self.vocab, self.moves, self.model), None, None)


cdef class BeamDependencyParser(BeamParser):
    TransitionSystem = ArcEager

    feature_templates = get_feature_templates('basic')

    def add_label(self, label):
        Parser.add_label(self, label)
        if isinstance(label, basestring):
            label = self.vocab.strings[label]


__all__ = ['Tagger', 'DependencyParser', 'EntityRecognizer', 'BeamDependencyParser',
           'BeamEntityRecognizer', 'TokenVectorEnoder']
