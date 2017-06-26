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
from ._ml import rebatch, Tok2Vec, flatten, get_col, doc2feats
from .parts_of_speech import X


class TokenVectorEncoder(object):
    """Assign position-sensitive vectors to tokens, using a CNN or RNN."""
    name = 'tensorizer'

    @classmethod
    def Model(cls, width=128, embed_size=7500, **cfg):
        """Create a new statistical model for the class.

        width (int): Output size of the model.
        embed_size (int): Number of vectors in the embedding table.
        **cfg: Config parameters.
        RETURNS (Model): A `thinc.neural.Model` or similar instance.
        """
        width = util.env_opt('token_vector_width', width)
        embed_size = util.env_opt('embed_size', embed_size)
        return Tok2Vec(width, embed_size, preprocess=None)

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
        self.doc2feats = doc2feats()
        self.model = model

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
        feats = self.doc2feats(docs)
        tokvecs = self.model(feats)
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
        feats = self.doc2feats(docs)
        tokvecs, bp_tokvecs = self.model.begin_update(feats, drop=drop)
        return tokvecs, bp_tokvecs

    def get_loss(self, docs, golds, scores):
        # TODO: implement
        raise NotImplementedError

    def begin_training(self, gold_tuples, pipeline=None):
        """Allocate models, pre-process training data and acquire a trainer and
        optimizer.

        gold_tuples (iterable): Gold-standard training data.
        pipeline (list): The pipeline the model is part of.
        """
        self.doc2feats = doc2feats()
        if self.model is True:
            self.model = self.Model()

    def use_params(self, params):
        """Replace weights of models in the pipeline with those provided in the
        params dictionary.

        params (dict): A dictionary of parameters keyed by model ID.
        """
        with self.model.use_params(params):
            yield

    def to_bytes(self, **exclude):
        serialize = OrderedDict((
            ('model', lambda: self.model.to_bytes()),
            ('vocab', lambda: self.vocab.to_bytes())
        ))
        return util.to_bytes(serialize, exclude)

    def from_bytes(self, bytes_data, **exclude):
        if self.model is True:
            self.model = self.Model()
        deserialize = OrderedDict((
            ('model', lambda b: self.model.from_bytes(b)),
            ('vocab', lambda b: self.vocab.from_bytes(b))
        ))
        util.from_bytes(bytes_data, deserialize, exclude)
        return self

    def to_disk(self, path, **exclude):
        serialize = OrderedDict((
            ('model', lambda p: p.open('wb').write(self.model.to_bytes())),
            ('vocab', lambda p: self.vocab.to_disk(p))
        ))
        util.to_disk(path, serialize, exclude)

    def from_disk(self, path, **exclude):
        if self.model is True:
            self.model = self.Model()
        deserialize = OrderedDict((
            ('model', lambda p: self.model.from_bytes(p.open('rb').read())),
            ('vocab', lambda p: self.vocab.from_disk(p))
        ))
        util.from_disk(path, deserialize, exclude)
        return self


class NeuralTagger(object):
    name = 'tagger'
    def __init__(self, vocab, model=True):
        self.vocab = vocab
        self.model = model

    def __call__(self, doc):
        tags = self.predict([doc.tensor])
        self.set_annotations([doc], tags)
        return doc

    def pipe(self, stream, batch_size=128, n_threads=-1):
        for docs in cytoolz.partition_all(batch_size, stream):
            tokvecs = [d.tensor for d in docs]
            tag_ids = self.predict(tokvecs)
            self.set_annotations(docs, tag_ids)
            yield from docs

    def predict(self, tokvecs):
        scores = self.model(tokvecs)
        scores = self.model.ops.flatten(scores)
        guesses = scores.argmax(axis=1)
        if not isinstance(guesses, numpy.ndarray):
            guesses = guesses.get()
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
            for j, tag_id in enumerate(doc_tag_ids):
                # Don't clobber preset POS tags
                if doc.c[j].tag == 0 and doc.c[j].pos == 0:
                    vocab.morphology.assign_tag_id(&doc.c[j], tag_id)
                idx += 1
        doc.is_tagged = True

    def update(self, docs_tokvecs, golds, drop=0., sgd=None, losses=None):
        docs, tokvecs = docs_tokvecs

        if self.model.nI is None:
            self.model.nI = tokvecs[0].shape[1]

        tag_scores, bp_tag_scores = self.model.begin_update(tokvecs, drop=drop)
        loss, d_tag_scores = self.get_loss(docs, golds, tag_scores)

        d_tokvecs = bp_tag_scores(d_tag_scores, sgd=sgd)

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

    def begin_training(self, gold_tuples, pipeline=None):
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
            self.model = self.Model(self.vocab.morphology.n_tags, token_vector_width)

    @classmethod
    def Model(cls, n_tags, token_vector_width):
        return with_flatten(
            chain(Maxout(token_vector_width, token_vector_width),
                  Softmax(n_tags, token_vector_width)))

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
                token_vector_width = util.env_opt('token_vector_width', 128)
                self.model = self.Model(self.vocab.morphology.n_tags, token_vector_width)
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
        ))
        util.to_disk(path, serialize, exclude)

    def from_disk(self, path, **exclude):
        def load_model(p):
            if self.model is True:
                token_vector_width = util.env_opt('token_vector_width', 128)
                self.model = self.Model(self.vocab.morphology.n_tags, token_vector_width)
            self.model.from_bytes(p.open('rb').read())

        def load_tag_map(p):
            with p.open('rb') as file_:
                tag_map = msgpack.loads(file_.read(), encoding='utf8')
            self.vocab.morphology = Morphology(
                self.vocab.strings, tag_map=tag_map,
                lemmatizer=self.vocab.morphology.lemmatizer,
                exc=self.vocab.morphology.exc)

        deserialize = OrderedDict((
            ('vocab', lambda p: self.vocab.from_disk(p)),
            ('tag_map', load_tag_map),
            ('model', load_model),
        ))
        util.from_disk(path, deserialize, exclude)
        return self


class NeuralLabeller(NeuralTagger):
    name = 'nn_labeller'
    def __init__(self, vocab, model=True):
        self.vocab = vocab
        self.model = model
        self.labels = {}

    def set_annotations(self, docs, dep_ids):
        pass

    def begin_training(self, gold_tuples, pipeline=None):
        gold_tuples = nonproj.preprocess_training_data(gold_tuples)
        for raw_text, annots_brackets in gold_tuples:
            for annots, brackets in annots_brackets:
                ids, words, tags, heads, deps, ents = annots
                for dep in deps:
                    if dep not in self.labels:
                        self.labels[dep] = len(self.labels)
        token_vector_width = pipeline[0].model.nO
        if self.model is True:
            self.model = self.Model(len(self.labels), token_vector_width)

    @classmethod
    def Model(cls, n_tags, token_vector_width):
        return with_flatten(
            chain(Maxout(token_vector_width, token_vector_width),
                  Softmax(n_tags, token_vector_width)))

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


class SimilarityHook(object):
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
    def __init__(self, vocab, model=True):
        self.vocab = vocab
        self.model = model

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

    def begin_training(self, _, pipeline=None):
        """
        Allocate model, using width from tensorizer in pipeline.

        gold_tuples (iterable): Gold-standard training data.
        pipeline (list): The pipeline the model is part of.
        """
        if self.model is True:
            self.model = self.Model(pipeline[0].model.nO)

    def use_params(self, params):
        """Replace weights of models in the pipeline with those provided in the
        params dictionary.

        params (dict): A dictionary of parameters keyed by model ID.
        """
        with self.model.use_params(params):
            yield

    def to_bytes(self, **exclude):
        serialize = OrderedDict((
            ('model', lambda: self.model.to_bytes()),
            ('vocab', lambda: self.vocab.to_bytes())
        ))
        return util.to_bytes(serialize, exclude)

    def from_bytes(self, bytes_data, **exclude):
        if self.model is True:
            self.model = self.Model()
        deserialize = OrderedDict((
            ('model', lambda b: self.model.from_bytes(b)),
            ('vocab', lambda b: self.vocab.from_bytes(b))
        ))
        util.from_bytes(bytes_data, deserialize, exclude)
        return self

    def to_disk(self, path, **exclude):
        serialize = OrderedDict((
            ('model', lambda p: p.open('wb').write(self.model.to_bytes())),
            ('vocab', lambda p: self.vocab.to_disk(p))
        ))
        util.to_disk(path, serialize, exclude)

    def from_disk(self, path, **exclude):
        if self.model is True:
            self.model = self.Model()
        deserialize = OrderedDict((
            ('model', lambda p: self.model.from_bytes(p.open('rb').read())),
            ('vocab', lambda p: self.vocab.from_disk(p))
        ))
        util.from_disk(path, deserialize, exclude)
        return self


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
