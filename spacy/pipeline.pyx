# cython: infer_types=True
# cython: profile=True
# coding: utf8
from __future__ import unicode_literals

from thinc.api import chain, layerize, with_getitem
import numpy
cimport numpy as np
import cytoolz
import util
from collections import OrderedDict
import ujson
import msgpack

from thinc.api import add, layerize, chain, clone, concatenate, with_flatten
from thinc.v2v import Model, Maxout, Softmax, Affine, ReLu, SELU
from thinc.i2v import HashEmbed
from thinc.t2v import Pooling, max_pool, mean_pool, sum_pool
from thinc.t2t import ExtractWindow, ParametricAttention
from thinc.misc import Residual
from thinc.misc import BatchNorm as BN
from thinc.misc import LayerNorm as LN

from thinc.neural.util import to_categorical

from thinc.neural._classes.difference import Siamese, CauchySimilarity

from .tokens.doc cimport Doc
from .syntax.parser cimport Parser as LinearParser
from .syntax.nn_parser cimport Parser as NeuralParser
from .syntax import nonproj
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
from ._ml import link_vectors_to_models
from .parts_of_speech import X


class SentenceSegmenter(object):
    """A simple spaCy hook, to allow custom sentence boundary detection logic
    (that doesn't require the dependency parse).

    To change the sentence boundary detection strategy, pass a generator
    function `strategy` on initialization, or assign a new strategy to
    the .strategy attribute.

    Sentence detection strategies should be generators that take `Doc` objects
    and yield `Span` objects for each sentence.
    """
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
        """Initialize a model for the pipe."""
        raise NotImplementedError

    def __init__(self, vocab, model=True, **cfg):
        """Create a new pipe instance."""
        raise NotImplementedError

    def __call__(self, doc):
        """Apply the pipe to one document. The document is
        modified in-place, and returned.

        Both __call__ and pipe should delegate to the `predict()`
        and `set_annotations()` methods.
        """
        scores = self.predict([doc])
        self.set_annotations([doc], scores)
        return doc

    def pipe(self, stream, batch_size=128, n_threads=-1):
        """Apply the pipe to a stream of documents.

        Both __call__ and pipe should delegate to the `predict()`
        and `set_annotations()` methods.
        """
        for docs in cytoolz.partition_all(batch_size, stream):
            docs = list(docs)
            scores = self.predict(docs)
            self.set_annotations(docs, scores)
            yield from docs

    def predict(self, docs):
        """Apply the pipeline's model to a batch of docs, without
        modifying them.
        """
        raise NotImplementedError

    def set_annotations(self, docs, scores):
        """Modify a batch of documents, using pre-computed scores."""
        raise NotImplementedError

    def update(self, docs, golds, drop=0., sgd=None, losses=None):
        """Learn from a batch of documents and gold-standard information,
        updating the pipe's model.

        Delegates to predict() and get_loss().
        """
        raise NotImplementedError

    def get_loss(self, docs, golds, scores):
        """Find the loss and gradient of loss for the batch of
        documents and their predicted scores."""
        raise NotImplementedError

    def begin_training(self, gold_tuples=tuple(), pipeline=None):
        """Initialize the pipe for training, using data exampes if available.
        If no model has been initialized yet, the model is added."""
        if self.model is True:
            self.model = self.Model(**self.cfg)
        link_vectors_to_models(self.vocab)

    def use_params(self, params):
        """Modify the pipe's model, to use the given parameter values.
        """
        with self.model.use_params(params):
            yield

    def to_bytes(self, **exclude):
        """Serialize the pipe to a bytestring."""
        serialize = OrderedDict((
            ('cfg', lambda: json_dumps(self.cfg)),
            ('model', lambda: self.model.to_bytes()),
            ('vocab', lambda: self.vocab.to_bytes())
        ))
        return util.to_bytes(serialize, exclude)

    def from_bytes(self, bytes_data, **exclude):
        """Load the pipe from a bytestring."""
        def load_model(b):
            if self.model is True:
                self.cfg['pretrained_dims'] = self.vocab.vectors_length
                self.model = self.Model(**self.cfg)
            self.model.from_bytes(b)

        deserialize = OrderedDict((
            ('cfg', lambda b: self.cfg.update(ujson.loads(b))),
            ('vocab', lambda b: self.vocab.from_bytes(b)),
            ('model', load_model),
        ))
        util.from_bytes(bytes_data, deserialize, exclude)
        return self

    def to_disk(self, path, **exclude):
        """Serialize the pipe to disk."""
        serialize = OrderedDict((
            ('cfg', lambda p: p.open('w').write(json_dumps(self.cfg))),
            ('vocab', lambda p: self.vocab.to_disk(p)),
            ('model', lambda p: p.open('wb').write(self.model.to_bytes())),
        ))
        util.to_disk(path, serialize, exclude)

    def from_disk(self, path, **exclude):
        """Load the pipe from disk."""
        def load_model(p):
            if self.model is True:
                self.cfg['pretrained_dims'] = self.vocab.vectors_length
                self.model = self.Model(**self.cfg)
            self.model.from_bytes(p.open('rb').read())

        deserialize = OrderedDict((
            ('cfg', lambda p: self.cfg.update(_load_cfg(p))),
            ('vocab', lambda p: self.vocab.from_disk(p)),
            ('model', load_model),
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
        self.cfg.setdefault('cnn_maxout_pieces', 3)

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
            self.cfg['pretrained_dims'] = self.vocab.vectors_length
            self.model = self.Model(**self.cfg)
        link_vectors_to_models(self.vocab)


class NeuralTagger(BaseThincComponent):
    name = 'tagger'
    def __init__(self, vocab, model=True, **cfg):
        self.vocab = vocab
        self.model = model
        self.cfg = dict(cfg)
        self.cfg.setdefault('cnn_maxout_pieces', 2)
        self.cfg.setdefault('pretrained_dims', self.vocab.vectors.data.shape[1])

    def __call__(self, doc):
        tags = self.predict([doc])
        self.set_annotations([doc], tags)
        return doc

    def pipe(self, stream, batch_size=128, n_threads=-1):
        for docs in cytoolz.partition_all(batch_size, stream):
            docs = list(docs)
            tag_ids = self.predict(docs)
            self.set_annotations(docs, tag_ids)
            yield from docs

    def predict(self, docs):
        scores = self.model(docs)
        scores = self.model.ops.flatten(scores)
        guesses = scores.argmax(axis=1)
        if not isinstance(guesses, numpy.ndarray):
            guesses = guesses.get()
        guesses = self.model.ops.unflatten(guesses,
                    [len(d) for d in docs])
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

    def update(self, docs, golds, drop=0., sgd=None, losses=None):
        if losses is not None and self.name not in losses:
            losses[self.name] = 0.

        tag_scores, bp_tag_scores = self.model.begin_update(docs, drop=drop)
        loss, d_tag_scores = self.get_loss(docs, golds, tag_scores)
        bp_tag_scores(d_tag_scores, sgd=sgd)

        if losses is not None:
            losses[self.name] += loss

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
        if self.model is True:
            self.cfg['pretrained_dims'] = self.vocab.vectors.data.shape[1]
            self.model = self.Model(self.vocab.morphology.n_tags, **self.cfg)
        link_vectors_to_models(self.vocab)

    @classmethod
    def Model(cls, n_tags, **cfg):
        return build_tagger_model(n_tags, **cfg)

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
                self.model = self.Model(self.vocab.morphology.n_tags, **self.cfg)
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
        self.cfg['pretrained_dims'] = self.vocab.vectors.data.shape[1]
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
                self.model = self.Model(self.vocab.morphology.n_tags, **self.cfg)
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
    def __init__(self, vocab, model=True, target='dep_tag_offset', **cfg):
        self.vocab = vocab
        self.model = model
        if target == 'dep':
            self.make_label = self.make_dep
        elif target == 'tag':
            self.make_label = self.make_tag
        elif target == 'ent':
            self.make_label = self.make_ent
        elif target == 'dep_tag_offset':
            self.make_label = self.make_dep_tag_offset
        elif target == 'ent_tag':
            self.make_label = self.make_ent_tag
        elif hasattr(target, '__call__'):
            self.make_label = target
        else:
            raise ValueError(
                "NeuralLabeller target should be function or one of "
                "['dep', 'tag', 'ent', 'dep_tag_offset', 'ent_tag']")
        self.cfg = dict(cfg)
        self.cfg.setdefault('cnn_maxout_pieces', 2)
        self.cfg.setdefault('pretrained_dims', self.vocab.vectors.data.shape[1])

    @property
    def labels(self):
        return self.cfg.setdefault('labels', {})

    @labels.setter
    def labels(self, value):
        self.cfg['labels'] = value

    def set_annotations(self, docs, dep_ids):
        pass

    def begin_training(self, gold_tuples=tuple(), pipeline=None, tok2vec=None):
        gold_tuples = nonproj.preprocess_training_data(gold_tuples)
        for raw_text, annots_brackets in gold_tuples:
            for annots, brackets in annots_brackets:
                ids, words, tags, heads, deps, ents = annots
                for i in range(len(ids)):
                    label = self.make_label(i, words, tags, heads, deps, ents)
                    if label is not None and label not in self.labels:
                        self.labels[label] = len(self.labels)
        print(len(self.labels))
        if self.model is True:
            token_vector_width = util.env_opt('token_vector_width')
            self.model = chain(
                tok2vec,
                Softmax(len(self.labels), token_vector_width)
            )
        link_vectors_to_models(self.vocab)

    @classmethod
    def Model(cls, n_tags, tok2vec=None, **cfg):
        return build_tagger_model(n_tags, tok2vec=tok2vec, **cfg)

    def get_loss(self, docs, golds, scores):
        cdef int idx = 0
        correct = numpy.zeros((scores.shape[0],), dtype='i')
        guesses = scores.argmax(axis=1)
        for gold in golds:
            for i in range(len(gold.labels)):
                label = self.make_label(i, gold.words, gold.tags, gold.heads,
                                        gold.labels, gold.ents)
                if label is None or label not in self.labels:
                    correct[idx] = guesses[idx]
                else:
                    correct[idx] = self.labels[label]
                idx += 1
        correct = self.model.ops.xp.array(correct, dtype='i')
        d_scores = scores - to_categorical(correct, nb_classes=scores.shape[1])
        d_scores /= d_scores.shape[0]
        loss = (d_scores**2).sum()
        return float(loss), d_scores

    @staticmethod
    def make_dep(i, words, tags, heads, deps, ents):
        if deps[i] is None or heads[i] is None:
            return None
        return deps[i]

    @staticmethod
    def make_tag(i, words, tags, heads, deps, ents):
        return tags[i]

    @staticmethod
    def make_ent(i, words, tags, heads, deps, ents):
        if ents is None:
            return None
        return ents[i]

    @staticmethod
    def make_dep_tag_offset(i, words, tags, heads, deps, ents):
        if deps[i] is None or heads[i] is None:
            return None
        offset = heads[i] - i
        offset = min(offset, 2)
        offset = max(offset, -2)
        return '%s-%s:%d' % (deps[i], tags[i], offset)

    @staticmethod
    def make_ent_tag(i, words, tags, heads, deps, ents):
        if ents is None or ents[i] is None:
            return None
        else:
            return '%s-%s' % (tags[i], ents[i])


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
        """Install similarity hook"""
        doc.user_hooks['similarity'] = self.predict
        return doc

    def pipe(self, docs, **kwargs):
        for doc in docs:
            yield self(doc)

    def predict(self, doc1, doc2):
        return self.model.predict([(doc1, doc2)])

    def update(self, doc1_doc2, golds, sgd=None, drop=0.):
        sims, bp_sims = self.model.begin_update(doc1_doc2, drop=drop)

    def begin_training(self, _=tuple(), pipeline=None):
        """
        Allocate model, using width from tensorizer in pipeline.

        gold_tuples (iterable): Gold-standard training data.
        pipeline (list): The pipeline the model is part of.
        """
        if self.model is True:
            self.model = self.Model(pipeline[0].model.nO)
            link_vectors_to_models(self.vocab)


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

    def update(self, docs, golds, state=None, drop=0., sgd=None, losses=None):
        scores, bp_scores = self.model.begin_update(docs, drop=drop)
        loss, d_scores = self.get_loss(docs, golds, scores)
        bp_scores(d_scores, sgd=sgd)
        if losses is not None:
            losses.setdefault(self.name, 0.0)
            losses[self.name] += loss

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
            link_vectors_to_models(self.vocab)


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

    @property
    def postprocesses(self):
        return [nonproj.deprojectivize]


cdef class NeuralDependencyParser(NeuralParser):
    name = 'parser'
    TransitionSystem = ArcEager

    @property
    def postprocesses(self):
        return [nonproj.deprojectivize]

    def init_multitask_objectives(self, gold_tuples, pipeline, **cfg):
        for target in []:
            labeller = NeuralLabeller(self.vocab, target=target)
            tok2vec = self.model[0]
            labeller.begin_training(gold_tuples, pipeline=pipeline, tok2vec=tok2vec)
            pipeline.append(labeller)
            self._multitasks.append(labeller)

    def __reduce__(self):
        return (NeuralDependencyParser, (self.vocab, self.moves, self.model), None, None)


cdef class NeuralEntityRecognizer(NeuralParser):
    name = 'ner'
    TransitionSystem = BiluoPushDown

    nr_feature = 6

    def init_multitask_objectives(self, gold_tuples, pipeline, **cfg):
        for target in []:
            labeller = NeuralLabeller(self.vocab, target=target)
            tok2vec = self.model[0]
            labeller.begin_training(gold_tuples, pipeline=pipeline, tok2vec=tok2vec)
            pipeline.append(labeller)
            self._multitasks.append(labeller)

    def __reduce__(self):
        return (NeuralEntityRecognizer, (self.vocab, self.moves, self.model), None, None)


cdef class BeamDependencyParser(BeamParser):
    TransitionSystem = ArcEager

    feature_templates = get_feature_templates('basic')

    def add_label(self, label):
        Parser.add_label(self, label)
        if isinstance(label, basestring):
            label = self.vocab.strings[label]

    @property
    def postprocesses(self):
        return [nonproj.deprojectivize]



__all__ = ['Tagger', 'DependencyParser', 'EntityRecognizer', 'BeamDependencyParser',
           'BeamEntityRecognizer', 'TokenVectorEnoder']
