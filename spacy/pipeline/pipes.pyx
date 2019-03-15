# cython: infer_types=True
# cython: profile=True
# coding: utf8
from __future__ import unicode_literals

cimport numpy as np

import numpy
import srsly
from collections import OrderedDict
from thinc.api import chain
from thinc.v2v import Affine, Maxout, Softmax
from thinc.misc import LayerNorm
from thinc.neural.util import to_categorical, copy_array

from ..tokens.doc cimport Doc
from ..syntax.nn_parser cimport Parser
from ..syntax.ner cimport BiluoPushDown
from ..syntax.arc_eager cimport ArcEager
from ..morphology cimport Morphology
from ..vocab cimport Vocab

from ..syntax import nonproj
from ..attrs import POS, ID
from ..parts_of_speech import X
from .._ml import Tok2Vec, build_tagger_model
from .._ml import build_text_classifier, build_simple_cnn_text_classifier
from .._ml import link_vectors_to_models, zero_init, flatten
from .._ml import masked_language_model, create_default_optimizer
from ..errors import Errors, TempErrors
from .. import util


def _load_cfg(path):
    if path.exists():
        return srsly.read_json(path)
    else:
        return {}


class Pipe(object):
    """This class is not instantiated directly. Components inherit from it, and
    it defines the interface that components should follow to function as
    components in a spaCy analysis pipeline.
    """

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
        self.require_model()
        scores, tensors = self.predict([doc])
        self.set_annotations([doc], scores, tensors=tensors)
        return doc

    def require_model(self):
        """Raise an error if the component's model is not initialized."""
        if getattr(self, "model", None) in (None, True, False):
            raise ValueError(Errors.E109.format(name=self.name))

    def pipe(self, stream, batch_size=128, n_threads=-1):
        """Apply the pipe to a stream of documents.

        Both __call__ and pipe should delegate to the `predict()`
        and `set_annotations()` methods.
        """
        for docs in util.minibatch(stream, size=batch_size):
            docs = list(docs)
            scores, tensors = self.predict(docs)
            self.set_annotations(docs, scores, tensor=tensors)
            yield from docs

    def predict(self, docs):
        """Apply the pipeline's model to a batch of docs, without
        modifying them.
        """
        self.require_model()
        raise NotImplementedError

    def set_annotations(self, docs, scores, tensors=None):
        """Modify a batch of documents, using pre-computed scores."""
        raise NotImplementedError

    def update(self, docs, golds, drop=0.0, sgd=None, losses=None):
        """Learn from a batch of documents and gold-standard information,
        updating the pipe's model.

        Delegates to predict() and get_loss().
        """
        self.require_model()
        raise NotImplementedError

    def rehearse(self, docs, sgd=None, losses=None, **config):
        pass

    def get_loss(self, docs, golds, scores):
        """Find the loss and gradient of loss for the batch of
        documents and their predicted scores."""
        raise NotImplementedError

    def add_label(self, label):
        """Add an output label, to be predicted by the model.

        It's possible to extend pre-trained models with new labels,
        but care should be taken to avoid the "catastrophic forgetting"
        problem.
        """
        raise NotImplementedError

    def create_optimizer(self):
        return create_default_optimizer(self.model.ops, **self.cfg.get("optimizer", {}))

    def begin_training(
        self, get_gold_tuples=lambda: [], pipeline=None, sgd=None, **kwargs
    ):
        """Initialize the pipe for training, using data exampes if available.
        If no model has been initialized yet, the model is added."""
        if self.model is True:
            self.model = self.Model(**self.cfg)
        link_vectors_to_models(self.vocab)
        if sgd is None:
            sgd = self.create_optimizer()
        return sgd

    def use_params(self, params):
        """Modify the pipe's model, to use the given parameter values."""
        with self.model.use_params(params):
            yield

    def to_bytes(self, exclude=tuple(), **kwargs):
        """Serialize the pipe to a bytestring.

        exclude (list): String names of serialization fields to exclude.
        RETURNS (bytes): The serialized object.
        """
        serialize = OrderedDict()
        serialize["cfg"] = lambda: srsly.json_dumps(self.cfg)
        if self.model not in (True, False, None):
            serialize["model"] = self.model.to_bytes
        serialize["vocab"] = self.vocab.to_bytes
        exclude = util.get_serialization_exclude(serialize, exclude, kwargs)
        return util.to_bytes(serialize, exclude)

    def from_bytes(self, bytes_data, exclude=tuple(), **kwargs):
        """Load the pipe from a bytestring."""

        def load_model(b):
            # TODO: Remove this once we don't have to handle previous models
            if self.cfg.get("pretrained_dims") and "pretrained_vectors" not in self.cfg:
                self.cfg["pretrained_vectors"] = self.vocab.vectors.name
            if self.model is True:
                self.model = self.Model(**self.cfg)
            self.model.from_bytes(b)

        deserialize = OrderedDict()
        deserialize["cfg"] = lambda b: self.cfg.update(srsly.json_loads(b))
        deserialize["vocab"] = lambda b: self.vocab.from_bytes(b)
        deserialize["model"] = load_model
        exclude = util.get_serialization_exclude(deserialize, exclude, kwargs)
        util.from_bytes(bytes_data, deserialize, exclude)
        return self

    def to_disk(self, path, exclude=tuple(), **kwargs):
        """Serialize the pipe to disk."""
        serialize = OrderedDict()
        serialize["cfg"] = lambda p: srsly.write_json(p, self.cfg)
        serialize["vocab"] = lambda p: self.vocab.to_disk(p)
        if self.model not in (None, True, False):
            serialize["model"] = lambda p: p.open("wb").write(self.model.to_bytes())
        exclude = util.get_serialization_exclude(serialize, exclude, kwargs)
        util.to_disk(path, serialize, exclude)

    def from_disk(self, path, exclude=tuple(), **kwargs):
        """Load the pipe from disk."""

        def load_model(p):
            # TODO: Remove this once we don't have to handle previous models
            if self.cfg.get("pretrained_dims") and "pretrained_vectors" not in self.cfg:
                self.cfg["pretrained_vectors"] = self.vocab.vectors.name
            if self.model is True:
                self.model = self.Model(**self.cfg)
            self.model.from_bytes(p.open("rb").read())

        deserialize = OrderedDict()
        deserialize["cfg"] = lambda p: self.cfg.update(_load_cfg(p))
        deserialize["vocab"] = lambda p: self.vocab.from_disk(p)
        deserialize["model"] = load_model
        exclude = util.get_serialization_exclude(deserialize, exclude, kwargs)
        util.from_disk(path, deserialize, exclude)
        return self


class Tensorizer(Pipe):
    """Pre-train position-sensitive vectors for tokens."""

    name = "tensorizer"

    @classmethod
    def Model(cls, output_size=300, **cfg):
        """Create a new statistical model for the class.

        width (int): Output size of the model.
        embed_size (int): Number of vectors in the embedding table.
        **cfg: Config parameters.
        RETURNS (Model): A `thinc.neural.Model` or similar instance.
        """
        input_size = util.env_opt("token_vector_width", cfg.get("input_size", 96))
        return zero_init(Affine(output_size, input_size, drop_factor=0.0))

    def __init__(self, vocab, model=True, **cfg):
        """Construct a new statistical model. Weights are not allocated on
        initialisation.

        vocab (Vocab): A `Vocab` instance. The model must share the same
            `Vocab` instance with the `Doc` objects it will process.
        model (Model): A `Model` instance or `True` allocate one later.
        **cfg: Config parameters.

        EXAMPLE:
            >>> from spacy.pipeline import TokenVectorEncoder
            >>> tok2vec = TokenVectorEncoder(nlp.vocab)
            >>> tok2vec.model = tok2vec.Model(128, 5000)
        """
        self.vocab = vocab
        self.model = model
        self.input_models = []
        self.cfg = dict(cfg)
        self.cfg.setdefault("cnn_maxout_pieces", 3)

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
        YIELDS (iterator): A sequence of `Doc` objects, in order of input.
        """
        for docs in util.minibatch(stream, size=batch_size):
            docs = list(docs)
            tensors = self.predict(docs)
            self.set_annotations(docs, tensors)
            yield from docs

    def predict(self, docs):
        """Return a single tensor for a batch of documents.

        docs (iterable): A sequence of `Doc` objects.
        RETURNS (object): Vector representations for each token in the docs.
        """
        self.require_model()
        inputs = self.model.ops.flatten([doc.tensor for doc in docs])
        outputs = self.model(inputs)
        return self.model.ops.unflatten(outputs, [len(d) for d in docs])

    def set_annotations(self, docs, tensors):
        """Set the tensor attribute for a batch of documents.

        docs (iterable): A sequence of `Doc` objects.
        tensors (object): Vector representation for each token in the docs.
        """
        for doc, tensor in zip(docs, tensors):
            if tensor.shape[0] != len(doc):
                raise ValueError(Errors.E076.format(rows=tensor.shape[0], words=len(doc)))
            doc.tensor = tensor

    def update(self, docs, golds, state=None, drop=0.0, sgd=None, losses=None):
        """Update the model.

        docs (iterable): A batch of `Doc` objects.
        golds (iterable): A batch of `GoldParse` objects.
        drop (float): The droput rate.
        sgd (callable): An optimizer.
        RETURNS (dict): Results from the update.
        """
        self.require_model()
        if isinstance(docs, Doc):
            docs = [docs]
        inputs = []
        bp_inputs = []
        for tok2vec in self.input_models:
            tensor, bp_tensor = tok2vec.begin_update(docs, drop=drop)
            inputs.append(tensor)
            bp_inputs.append(bp_tensor)
        inputs = self.model.ops.xp.hstack(inputs)
        scores, bp_scores = self.model.begin_update(inputs, drop=drop)
        loss, d_scores = self.get_loss(docs, golds, scores)
        d_inputs = bp_scores(d_scores, sgd=sgd)
        d_inputs = self.model.ops.xp.split(d_inputs, len(self.input_models), axis=1)
        for d_input, bp_input in zip(d_inputs, bp_inputs):
            bp_input(d_input, sgd=sgd)
        if losses is not None:
            losses.setdefault(self.name, 0.0)
            losses[self.name] += loss
        return loss

    def get_loss(self, docs, golds, prediction):
        ids = self.model.ops.flatten([doc.to_array(ID).ravel() for doc in docs])
        target = self.vocab.vectors.data[ids]
        d_scores = (prediction - target) / prediction.shape[0]
        loss = (d_scores ** 2).sum()
        return loss, d_scores

    def begin_training(self, gold_tuples=lambda: [], pipeline=None, sgd=None, **kwargs):
        """Allocate models, pre-process training data and acquire an
        optimizer.

        gold_tuples (iterable): Gold-standard training data.
        pipeline (list): The pipeline the model is part of.
        """
        if pipeline is not None:
            for name, model in pipeline:
                if getattr(model, "tok2vec", None):
                    self.input_models.append(model.tok2vec)
        if self.model is True:
            self.model = self.Model(**self.cfg)
        link_vectors_to_models(self.vocab)
        if sgd is None:
            sgd = self.create_optimizer()
        return sgd


class Tagger(Pipe):
    """Pipeline component for part-of-speech tagging.

    DOCS: https://spacy.io/api/tagger
    """

    name = "tagger"

    def __init__(self, vocab, model=True, **cfg):
        self.vocab = vocab
        self.model = model
        self._rehearsal_model = None
        self.cfg = OrderedDict(sorted(cfg.items()))
        self.cfg.setdefault("cnn_maxout_pieces", 2)

    @property
    def labels(self):
        return tuple(self.vocab.morphology.tag_names)

    @property
    def tok2vec(self):
        if self.model in (None, True, False):
            return None
        else:
            return chain(self.model.tok2vec, flatten)

    def __call__(self, doc):
        tags, tokvecs = self.predict([doc])
        self.set_annotations([doc], tags, tensors=tokvecs)
        return doc

    def pipe(self, stream, batch_size=128, n_threads=-1):
        for docs in util.minibatch(stream, size=batch_size):
            docs = list(docs)
            tag_ids, tokvecs = self.predict(docs)
            self.set_annotations(docs, tag_ids, tensors=tokvecs)
            yield from docs

    def predict(self, docs):
        self.require_model()
        if not any(len(doc) for doc in docs):
            # Handle case where there are no tokens in any docs.
            n_labels = len(self.labels)
            guesses = [self.model.ops.allocate((0, n_labels)) for doc in docs]
            tokvecs = self.model.ops.allocate((0, self.model.tok2vec.nO))
            return guesses, tokvecs
        tokvecs = self.model.tok2vec(docs)
        scores = self.model.softmax(tokvecs)
        guesses = []
        for doc_scores in scores:
            doc_guesses = doc_scores.argmax(axis=1)
            if not isinstance(doc_guesses, numpy.ndarray):
                doc_guesses = doc_guesses.get()
            guesses.append(doc_guesses)
        return guesses, tokvecs

    def set_annotations(self, docs, batch_tag_ids, tensors=None):
        if isinstance(docs, Doc):
            docs = [docs]
        cdef Doc doc
        cdef int idx = 0
        cdef Vocab vocab = self.vocab
        for i, doc in enumerate(docs):
            doc_tag_ids = batch_tag_ids[i]
            if hasattr(doc_tag_ids, "get"):
                doc_tag_ids = doc_tag_ids.get()
            for j, tag_id in enumerate(doc_tag_ids):
                # Don't clobber preset POS tags
                if doc.c[j].tag == 0 and doc.c[j].pos == 0:
                    # Don't clobber preset lemmas
                    lemma = doc.c[j].lemma
                    vocab.morphology.assign_tag_id(&doc.c[j], tag_id)
                    if lemma != 0 and lemma != doc.c[j].lex.orth:
                        doc.c[j].lemma = lemma
                idx += 1
            if tensors is not None and len(tensors):
                if isinstance(doc.tensor, numpy.ndarray) \
                and not isinstance(tensors[i], numpy.ndarray):
                    doc.extend_tensor(tensors[i].get())
                else:
                    doc.extend_tensor(tensors[i])
            doc.is_tagged = True

    def update(self, docs, golds, drop=0., sgd=None, losses=None):
        self.require_model()
        if losses is not None and self.name not in losses:
            losses[self.name] = 0.

        tag_scores, bp_tag_scores = self.model.begin_update(docs, drop=drop)
        loss, d_tag_scores = self.get_loss(docs, golds, tag_scores)
        bp_tag_scores(d_tag_scores, sgd=sgd)

        if losses is not None:
            losses[self.name] += loss

    def rehearse(self, docs, drop=0., sgd=None, losses=None):
        """Perform a 'rehearsal' update, where we try to match the output of
        an initial model.
        """
        if self._rehearsal_model is None:
            return
        guesses, backprop = self.model.begin_update(docs, drop=drop)
        target = self._rehearsal_model(docs)
        gradient = guesses - target
        backprop(gradient, sgd=sgd)
        if losses is not None:
            losses.setdefault(self.name, 0.0)
            losses[self.name] += (gradient**2).sum()

    def get_loss(self, docs, golds, scores):
        scores = self.model.ops.flatten(scores)
        tag_index = {tag: i for i, tag in enumerate(self.labels)}
        cdef int idx = 0
        correct = numpy.zeros((scores.shape[0],), dtype="i")
        guesses = scores.argmax(axis=1)
        known_labels = numpy.ones((scores.shape[0], 1), dtype="f")
        for gold in golds:
            for tag in gold.tags:
                if tag is None:
                    correct[idx] = guesses[idx]
                elif tag in tag_index:
                    correct[idx] = tag_index[tag]
                else:
                    correct[idx] = 0
                    known_labels[idx] = 0.
                idx += 1
        correct = self.model.ops.xp.array(correct, dtype="i")
        d_scores = scores - to_categorical(correct, nb_classes=scores.shape[1])
        d_scores *= self.model.ops.asarray(known_labels)
        loss = (d_scores**2).sum()
        d_scores = self.model.ops.unflatten(d_scores, [len(d) for d in docs])
        return float(loss), d_scores

    def begin_training(self, get_gold_tuples=lambda: [], pipeline=None, sgd=None,
                       **kwargs):
        orig_tag_map = dict(self.vocab.morphology.tag_map)
        new_tag_map = OrderedDict()
        for raw_text, annots_brackets in get_gold_tuples():
            for annots, brackets in annots_brackets:
                ids, words, tags, heads, deps, ents = annots
                for tag in tags:
                    if tag in orig_tag_map:
                        new_tag_map[tag] = orig_tag_map[tag]
                    else:
                        new_tag_map[tag] = {POS: X}
        cdef Vocab vocab = self.vocab
        if new_tag_map:
            vocab.morphology = Morphology(vocab.strings, new_tag_map,
                                          vocab.morphology.lemmatizer,
                                          exc=vocab.morphology.exc)
        self.cfg["pretrained_vectors"] = kwargs.get("pretrained_vectors")
        if self.model is True:
            for hp in ["token_vector_width", "conv_depth"]:
                if hp in kwargs:
                    self.cfg[hp] = kwargs[hp]
            self.model = self.Model(self.vocab.morphology.n_tags, **self.cfg)
        link_vectors_to_models(self.vocab)
        if sgd is None:
            sgd = self.create_optimizer()
        return sgd

    @classmethod
    def Model(cls, n_tags, **cfg):
        if cfg.get("pretrained_dims") and not cfg.get("pretrained_vectors"):
            raise ValueError(TempErrors.T008)
        return build_tagger_model(n_tags, **cfg)

    def add_label(self, label, values=None):
        if label in self.labels:
            return 0
        if self.model not in (True, False, None):
            # Here's how the model resizing will work, once the
            # neuron-to-tag mapping is no longer controlled by
            # the Morphology class, which sorts the tag names.
            # The sorting makes adding labels difficult.
            # smaller = self.model._layers[-1]
            # larger = Softmax(len(self.labels)+1, smaller.nI)
            # copy_array(larger.W[:smaller.nO], smaller.W)
            # copy_array(larger.b[:smaller.nO], smaller.b)
            # self.model._layers[-1] = larger
            raise ValueError(TempErrors.T003)
        tag_map = dict(self.vocab.morphology.tag_map)
        if values is None:
            values = {POS: "X"}
        tag_map[label] = values
        self.vocab.morphology = Morphology(
            self.vocab.strings, tag_map=tag_map,
            lemmatizer=self.vocab.morphology.lemmatizer,
            exc=self.vocab.morphology.exc)
        return 1

    def use_params(self, params):
        with self.model.use_params(params):
            yield

    def to_bytes(self, exclude=tuple(), **kwargs):
        serialize = OrderedDict()
        if self.model not in (None, True, False):
            serialize["model"] = self.model.to_bytes
        serialize["vocab"] = self.vocab.to_bytes
        serialize["cfg"] = lambda: srsly.json_dumps(self.cfg)
        tag_map = OrderedDict(sorted(self.vocab.morphology.tag_map.items()))
        serialize["tag_map"] = lambda: srsly.msgpack_dumps(tag_map)
        exclude = util.get_serialization_exclude(serialize, exclude, kwargs)
        return util.to_bytes(serialize, exclude)

    def from_bytes(self, bytes_data, exclude=tuple(), **kwargs):
        def load_model(b):
            # TODO: Remove this once we don't have to handle previous models
            if self.cfg.get("pretrained_dims") and "pretrained_vectors" not in self.cfg:
                self.cfg["pretrained_vectors"] = self.vocab.vectors.name
            if self.model is True:
                token_vector_width = util.env_opt(
                    "token_vector_width",
                    self.cfg.get("token_vector_width", 96))
                self.model = self.Model(self.vocab.morphology.n_tags, **self.cfg)
            self.model.from_bytes(b)

        def load_tag_map(b):
            tag_map = srsly.msgpack_loads(b)
            self.vocab.morphology = Morphology(
                self.vocab.strings, tag_map=tag_map,
                lemmatizer=self.vocab.morphology.lemmatizer,
                exc=self.vocab.morphology.exc)

        deserialize = OrderedDict((
            ("vocab", lambda b: self.vocab.from_bytes(b)),
            ("tag_map", load_tag_map),
            ("cfg", lambda b: self.cfg.update(srsly.json_loads(b))),
            ("model", lambda b: load_model(b)),
        ))
        exclude = util.get_serialization_exclude(deserialize, exclude, kwargs)
        util.from_bytes(bytes_data, deserialize, exclude)
        return self

    def to_disk(self, path, exclude=tuple(), **kwargs):
        tag_map = OrderedDict(sorted(self.vocab.morphology.tag_map.items()))
        serialize = OrderedDict((
            ("vocab", lambda p: self.vocab.to_disk(p)),
            ("tag_map", lambda p: srsly.write_msgpack(p, tag_map)),
            ("model", lambda p: p.open("wb").write(self.model.to_bytes())),
            ("cfg", lambda p: srsly.write_json(p, self.cfg))
        ))
        exclude = util.get_serialization_exclude(serialize, exclude, kwargs)
        util.to_disk(path, serialize, exclude)

    def from_disk(self, path, exclude=tuple(), **kwargs):
        def load_model(p):
            # TODO: Remove this once we don't have to handle previous models
            if self.cfg.get("pretrained_dims") and "pretrained_vectors" not in self.cfg:
                self.cfg["pretrained_vectors"] = self.vocab.vectors.name
            if self.model is True:
                self.model = self.Model(self.vocab.morphology.n_tags, **self.cfg)
            with p.open("rb") as file_:
                self.model.from_bytes(file_.read())

        def load_tag_map(p):
            tag_map = srsly.read_msgpack(p)
            self.vocab.morphology = Morphology(
                self.vocab.strings, tag_map=tag_map,
                lemmatizer=self.vocab.morphology.lemmatizer,
                exc=self.vocab.morphology.exc)

        deserialize = OrderedDict((
            ("cfg", lambda p: self.cfg.update(_load_cfg(p))),
            ("vocab", lambda p: self.vocab.from_disk(p)),
            ("tag_map", load_tag_map),
            ("model", load_model),
        ))
        exclude = util.get_serialization_exclude(deserialize, exclude, kwargs)
        util.from_disk(path, deserialize, exclude)
        return self


class MultitaskObjective(Tagger):
    """Experimental: Assist training of a parser or tagger, by training a
    side-objective.
    """

    name = "nn_labeller"

    def __init__(self, vocab, model=True, target='dep_tag_offset', **cfg):
        self.vocab = vocab
        self.model = model
        if target == "dep":
            self.make_label = self.make_dep
        elif target == "tag":
            self.make_label = self.make_tag
        elif target == "ent":
            self.make_label = self.make_ent
        elif target == "dep_tag_offset":
            self.make_label = self.make_dep_tag_offset
        elif target == "ent_tag":
            self.make_label = self.make_ent_tag
        elif target == "sent_start":
            self.make_label = self.make_sent_start
        elif hasattr(target, "__call__"):
            self.make_label = target
        else:
            raise ValueError(Errors.E016)
        self.cfg = dict(cfg)
        self.cfg.setdefault("cnn_maxout_pieces", 2)

    @property
    def labels(self):
        return self.cfg.setdefault("labels", {})

    @labels.setter
    def labels(self, value):
        self.cfg["labels"] = value

    def set_annotations(self, docs, dep_ids, tensors=None):
        pass

    def begin_training(self, get_gold_tuples=lambda: [], pipeline=None, tok2vec=None,
                       sgd=None, **kwargs):
        gold_tuples = nonproj.preprocess_training_data(get_gold_tuples())
        for raw_text, annots_brackets in gold_tuples:
            for annots, brackets in annots_brackets:
                ids, words, tags, heads, deps, ents = annots
                for i in range(len(ids)):
                    label = self.make_label(i, words, tags, heads, deps, ents)
                    if label is not None and label not in self.labels:
                        self.labels[label] = len(self.labels)
        if self.model is True:
            token_vector_width = util.env_opt("token_vector_width")
            self.model = self.Model(len(self.labels), tok2vec=tok2vec)
        link_vectors_to_models(self.vocab)
        if sgd is None:
            sgd = self.create_optimizer()
        return sgd

    @classmethod
    def Model(cls, n_tags, tok2vec=None, **cfg):
        token_vector_width = util.env_opt("token_vector_width", 96)
        softmax = Softmax(n_tags, token_vector_width*2)
        model = chain(
            tok2vec,
            LayerNorm(Maxout(token_vector_width*2, token_vector_width, pieces=3)),
            softmax
        )
        model.tok2vec = tok2vec
        model.softmax = softmax
        return model

    def predict(self, docs):
        self.require_model()
        tokvecs = self.model.tok2vec(docs)
        scores = self.model.softmax(tokvecs)
        return tokvecs, scores

    def get_loss(self, docs, golds, scores):
        if len(docs) != len(golds):
            raise ValueError(Errors.E077.format(value="loss", n_docs=len(docs),
                                                n_golds=len(golds)))
        cdef int idx = 0
        correct = numpy.zeros((scores.shape[0],), dtype="i")
        guesses = scores.argmax(axis=1)
        for i, gold in enumerate(golds):
            for j in range(len(docs[i])):
                # Handes alignment for tokenization differences
                label = self.make_label(j, gold.words, gold.tags,
                                        gold.heads, gold.labels, gold.ents)
                if label is None or label not in self.labels:
                    correct[idx] = guesses[idx]
                else:
                    correct[idx] = self.labels[label]
                idx += 1
        correct = self.model.ops.xp.array(correct, dtype="i")
        d_scores = scores - to_categorical(correct, nb_classes=scores.shape[1])
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
        return "%s-%s:%d" % (deps[i], tags[i], offset)

    @staticmethod
    def make_ent_tag(i, words, tags, heads, deps, ents):
        if ents is None or ents[i] is None:
            return None
        else:
            return "%s-%s" % (tags[i], ents[i])

    @staticmethod
    def make_sent_start(target, words, tags, heads, deps, ents, cache=True, _cache={}):
        """A multi-task objective for representing sentence boundaries,
        using BILU scheme. (O is impossible)

        The implementation of this method uses an internal cache that relies
        on the identity of the heads array, to avoid requiring a new piece
        of gold data. You can pass cache=False if you know the cache will
        do the wrong thing.
        """
        assert len(words) == len(heads)
        assert target < len(words), (target, len(words))
        if cache:
            if id(heads) in _cache:
                return _cache[id(heads)][target]
            else:
                for key in list(_cache.keys()):
                    _cache.pop(key)
            sent_tags = ["I-SENT"] * len(words)
            _cache[id(heads)] = sent_tags
        else:
            sent_tags = ["I-SENT"] * len(words)

        def _find_root(child):
            seen = set([child])
            while child is not None and heads[child] != child:
                seen.add(child)
                child = heads[child]
            return child

        sentences = {}
        for i in range(len(words)):
            root = _find_root(i)
            if root is None:
                sent_tags[i] = None
            else:
                sentences.setdefault(root, []).append(i)
        for root, span in sorted(sentences.items()):
            if len(span) == 1:
                sent_tags[span[0]] = "U-SENT"
            else:
                sent_tags[span[0]] = "B-SENT"
                sent_tags[span[-1]] = "L-SENT"
        return sent_tags[target]


class ClozeMultitask(Pipe):
    @classmethod
    def Model(cls, vocab, tok2vec, **cfg):
        output_size = vocab.vectors.data.shape[1]
        output_layer = chain(
            LayerNorm(Maxout(output_size, tok2vec.nO, pieces=3)),
            zero_init(Affine(output_size, output_size, drop_factor=0.0))
        )
        model = chain(tok2vec, output_layer)
        model = masked_language_model(vocab, model)
        model.tok2vec = tok2vec
        model.output_layer = output_layer
        return model

    def __init__(self, vocab, model=True, **cfg):
        self.vocab = vocab
        self.model = model
        self.cfg = cfg

    def set_annotations(self, docs, dep_ids, tensors=None):
        pass

    def begin_training(self, get_gold_tuples=lambda: [], pipeline=None,
                        tok2vec=None, sgd=None, **kwargs):
        link_vectors_to_models(self.vocab)
        if self.model is True:
            self.model = self.Model(self.vocab, tok2vec)
        X = self.model.ops.allocate((5, self.model.tok2vec.nO))
        self.model.output_layer.begin_training(X)
        if sgd is None:
            sgd = self.create_optimizer()
        return sgd

    def predict(self, docs):
        self.require_model()
        tokvecs = self.model.tok2vec(docs)
        vectors = self.model.output_layer(tokvecs)
        return tokvecs, vectors

    def get_loss(self, docs, vectors, prediction):
        # The simplest way to implement this would be to vstack the
        # token.vector values, but that's a bit inefficient, especially on GPU.
        # Instead we fetch the index into the vectors table for each of our tokens,
        # and look them up all at once. This prevents data copying.
        ids = self.model.ops.flatten([doc.to_array(ID).ravel() for doc in docs])
        target = vectors[ids]
        gradient = (prediction - target) / prediction.shape[0]
        loss = (gradient**2).sum()
        return float(loss), gradient

    def update(self, docs, golds, drop=0., sgd=None, losses=None):
        pass

    def rehearse(self, docs, drop=0., sgd=None, losses=None):
        self.require_model()
        if losses is not None and self.name not in losses:
            losses[self.name] = 0.
        predictions, bp_predictions = self.model.begin_update(docs, drop=drop)
        loss, d_predictions = self.get_loss(docs, self.vocab.vectors.data, predictions)
        bp_predictions(d_predictions, sgd=sgd)

        if losses is not None:
            losses[self.name] += loss


class TextCategorizer(Pipe):
    """Pipeline component for text classification.

    DOCS: https://spacy.io/api/textcategorizer
    """
    name = 'textcat'

    @classmethod
    def Model(cls, nr_class=1, **cfg):
        embed_size = util.env_opt("embed_size", 2000)
        if "token_vector_width" in cfg:
            token_vector_width = cfg["token_vector_width"]
        else:
            token_vector_width = util.env_opt("token_vector_width", 96)
        if cfg.get("architecture") == "simple_cnn":
            tok2vec = Tok2Vec(token_vector_width, embed_size, **cfg)
            return build_simple_cnn_text_classifier(tok2vec, nr_class, **cfg)
        else:
            return build_text_classifier(nr_class, **cfg)

    @property
    def tok2vec(self):
        if self.model in (None, True, False):
            return None
        else:
            return self.model.tok2vec

    def __init__(self, vocab, model=True, **cfg):
        self.vocab = vocab
        self.model = model
        self._rehearsal_model = None
        self.cfg = dict(cfg)

    @property
    def labels(self):
        return tuple(self.cfg.setdefault("labels", []))

    @labels.setter
    def labels(self, value):
        self.cfg["labels"] = tuple(value)

    def __call__(self, doc):
        scores, tensors = self.predict([doc])
        self.set_annotations([doc], scores, tensors=tensors)
        return doc

    def pipe(self, stream, batch_size=128, n_threads=-1):
        for docs in util.minibatch(stream, size=batch_size):
            docs = list(docs)
            scores, tensors = self.predict(docs)
            self.set_annotations(docs, scores, tensors=tensors)
            yield from docs

    def predict(self, docs):
        self.require_model()
        scores = self.model(docs)
        scores = self.model.ops.asarray(scores)
        tensors = [doc.tensor for doc in docs]
        return scores, tensors

    def set_annotations(self, docs, scores, tensors=None):
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

    def rehearse(self, docs, drop=0., sgd=None, losses=None):
        if self._rehearsal_model is None:
            return
        scores, bp_scores = self.model.begin_update(docs, drop=drop)
        target = self._rehearsal_model(docs)
        gradient = scores - target
        bp_scores(gradient, sgd=sgd)
        if losses is not None:
            losses.setdefault(self.name, 0.0)
            losses[self.name] += (gradient**2).sum()

    def get_loss(self, docs, golds, scores):
        truths = numpy.zeros((len(golds), len(self.labels)), dtype="f")
        not_missing = numpy.ones((len(golds), len(self.labels)), dtype="f")
        for i, gold in enumerate(golds):
            for j, label in enumerate(self.labels):
                if label in gold.cats:
                    truths[i, j] = gold.cats[label]
                else:
                    not_missing[i, j] = 0.
        truths = self.model.ops.asarray(truths)
        not_missing = self.model.ops.asarray(not_missing)
        d_scores = (scores-truths) / scores.shape[0]
        d_scores *= not_missing
        mean_square_error = (d_scores**2).sum(axis=1).mean()
        return float(mean_square_error), d_scores

    def add_label(self, label):
        if label in self.labels:
            return 0
        if self.model not in (None, True, False):
            # This functionality was available previously, but was broken.
            # The problem is that we resize the last layer, but the last layer
            # is actually just an ensemble. We're not resizing the child layers
            # - a huge problem.
            raise ValueError(Errors.E116)
            # smaller = self.model._layers[-1]
            # larger = Affine(len(self.labels)+1, smaller.nI)
            # copy_array(larger.W[:smaller.nO], smaller.W)
            # copy_array(larger.b[:smaller.nO], smaller.b)
            # self.model._layers[-1] = larger
        self.labels = tuple(list(self.labels) + [label])
        return 1

    def begin_training(self, get_gold_tuples=lambda: [], pipeline=None, sgd=None, **kwargs):
        if self.model is True:
            self.cfg["pretrained_vectors"] = kwargs.get("pretrained_vectors")
            self.model = self.Model(len(self.labels), **self.cfg)
            link_vectors_to_models(self.vocab)
        if sgd is None:
            sgd = self.create_optimizer()
        return sgd


cdef class DependencyParser(Parser):
    """Pipeline component for dependency parsing.

    DOCS: https://spacy.io/api/dependencyparser
    """

    name = "parser"
    TransitionSystem = ArcEager

    @property
    def postprocesses(self):
        return [nonproj.deprojectivize]

    def add_multitask_objective(self, target):
        if target == "cloze":
            cloze = ClozeMultitask(self.vocab)
            self._multitasks.append(cloze)
        else:
            labeller = MultitaskObjective(self.vocab, target=target)
            self._multitasks.append(labeller)

    def init_multitask_objectives(self, get_gold_tuples, pipeline, sgd=None, **cfg):
        for labeller in self._multitasks:
            tok2vec = self.model.tok2vec
            labeller.begin_training(get_gold_tuples, pipeline=pipeline,
                                    tok2vec=tok2vec, sgd=sgd)

    def __reduce__(self):
        return (DependencyParser, (self.vocab, self.moves, self.model), None, None)

    @property
    def labels(self):
        # Get the labels from the model by looking at the available moves
        return tuple(set(move.split("-")[1] for move in self.move_names))


cdef class EntityRecognizer(Parser):
    """Pipeline component for named entity recognition.

    DOCS: https://spacy.io/api/entityrecognizer
    """

    name = "ner"
    TransitionSystem = BiluoPushDown
    nr_feature = 6

    def add_multitask_objective(self, target):
        if target == "cloze":
            cloze = ClozeMultitask(self.vocab)
            self._multitasks.append(cloze)
        else:
            labeller = MultitaskObjective(self.vocab, target=target)
            self._multitasks.append(labeller)

    def init_multitask_objectives(self, get_gold_tuples, pipeline, sgd=None, **cfg):
        for labeller in self._multitasks:
            tok2vec = self.model.tok2vec
            labeller.begin_training(get_gold_tuples, pipeline=pipeline,
                                    tok2vec=tok2vec)

    def __reduce__(self):
        return (EntityRecognizer, (self.vocab, self.moves, self.model),
                None, None)

    @property
    def labels(self):
        # Get the labels from the model by looking at the available moves, e.g.
        # B-PERSON, I-PERSON, L-PERSON, U-PERSON
        return tuple(set(move.split("-")[1] for move in self.move_names
                if move[0] in ("B", "I", "L", "U")))


__all__ = ["Tagger", "DependencyParser", "EntityRecognizer", "Tensorizer", "TextCategorizer"]
