# cython: infer_types=True, profile=True
import numpy
import srsly
import random

from thinc.api import CosineDistance, to_categorical, get_array_module
from thinc.api import set_dropout_rate, SequenceCategoricalCrossentropy
import warnings

from ..tokens.doc cimport Doc
from ..syntax.nn_parser cimport Parser
from ..syntax.ner cimport BiluoPushDown
from ..syntax.arc_eager cimport ArcEager
from ..morphology cimport Morphology
from ..vocab cimport Vocab

from .defaults import default_tagger, default_parser,  default_ner,  default_textcat
from .defaults import default_nel, default_senter
from .functions import merge_subtokens
from ..language import Language, component
from ..syntax import nonproj
from ..gold.example import Example
from ..attrs import POS, ID
from ..util import link_vectors_to_models, create_default_optimizer
from ..parts_of_speech import X
from ..kb import KnowledgeBase
from ..errors import Errors, TempErrors, Warnings
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
    def from_nlp(cls, nlp, model, **cfg):
        return cls(nlp.vocab, model, **cfg)

    def __init__(self, vocab, model, **cfg):
        """Create a new pipe instance."""
        raise NotImplementedError

    def __call__(self, Doc doc):
        """Apply the pipe to one document. The document is
        modified in-place, and returned.

        Both __call__ and pipe should delegate to the `predict()`
        and `set_annotations()` methods.
        """
        scores = self.predict([doc])
        self.set_annotations([doc], scores)
        return doc

    def pipe(self, stream, batch_size=128):
        """Apply the pipe to a stream of documents.

        Both __call__ and pipe should delegate to the `predict()`
        and `set_annotations()` methods.
        """
        for docs in util.minibatch(stream, size=batch_size):
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

    def rehearse(self, examples, sgd=None, losses=None, **config):
        pass

    def get_loss(self, examples, scores):
        """Find the loss and gradient of loss for the batch of
        examples (with embedded docs) and their predicted scores."""
        raise NotImplementedError

    def add_label(self, label):
        """Add an output label, to be predicted by the model.

        It's possible to extend pretrained models with new labels,
        but care should be taken to avoid the "catastrophic forgetting"
        problem.
        """
        raise NotImplementedError

    def create_optimizer(self):
        return create_default_optimizer()

    def begin_training(
        self, get_examples=lambda: [], pipeline=None, sgd=None, **kwargs
    ):
        """Initialize the pipe for training, using data exampes if available.
        If no model has been initialized yet, the model is added."""
        self.model.initialize()
        if hasattr(self, "vocab"):
            link_vectors_to_models(self.vocab)
        if sgd is None:
            sgd = self.create_optimizer()
        return sgd

    def set_output(self, nO):
        if self.model.has_dim("nO") is not False:
            self.model.set_dim("nO", nO)
        if self.model.has_ref("output_layer"):
            self.model.get_ref("output_layer").set_dim("nO", nO)

    def get_gradients(self):
        """Get non-zero gradients of the model's parameters, as a dictionary
        keyed by the parameter ID. The values are (weights, gradients) tuples.
        """
        gradients = {}
        queue = [self.model]
        seen = set()
        for node in queue:
            if node.id in seen:
                continue
            seen.add(node.id)
            if hasattr(node, "_mem") and node._mem.gradient.any():
                gradients[node.id] = [node._mem.weights, node._mem.gradient]
            if hasattr(node, "_layers"):
                queue.extend(node._layers)
        return gradients

    def use_params(self, params):
        """Modify the pipe's model, to use the given parameter values."""
        with self.model.use_params(params):
            yield

    def to_bytes(self, exclude=tuple()):
        """Serialize the pipe to a bytestring.

        exclude (list): String names of serialization fields to exclude.
        RETURNS (bytes): The serialized object.
        """
        serialize = {}
        serialize["cfg"] = lambda: srsly.json_dumps(self.cfg)
        serialize["model"] = self.model.to_bytes
        if hasattr(self, "vocab"):
            serialize["vocab"] = self.vocab.to_bytes
        return util.to_bytes(serialize, exclude)

    def from_bytes(self, bytes_data, exclude=tuple()):
        """Load the pipe from a bytestring."""

        def load_model(b):
            try:
                self.model.from_bytes(b)
            except AttributeError:
                raise ValueError(Errors.E149)

        deserialize = {}
        if hasattr(self, "vocab"):
            deserialize["vocab"] = lambda b: self.vocab.from_bytes(b)
        deserialize["cfg"] = lambda b: self.cfg.update(srsly.json_loads(b))
        deserialize["model"] = load_model
        util.from_bytes(bytes_data, deserialize, exclude)
        return self

    def to_disk(self, path, exclude=tuple()):
        """Serialize the pipe to disk."""
        serialize = {}
        serialize["cfg"] = lambda p: srsly.write_json(p, self.cfg)
        serialize["vocab"] = lambda p: self.vocab.to_disk(p)
        serialize["model"] = lambda p: self.model.to_disk(p)
        util.to_disk(path, serialize, exclude)

    def from_disk(self, path, exclude=tuple()):
        """Load the pipe from disk."""

        def load_model(p):
            try:
                self.model.from_bytes(p.open("rb").read())
            except AttributeError:
                raise ValueError(Errors.E149)

        deserialize = {}
        deserialize["vocab"] = lambda p: self.vocab.from_disk(p)
        deserialize["cfg"] = lambda p: self.cfg.update(_load_cfg(p))
        deserialize["model"] = load_model
        util.from_disk(path, deserialize, exclude)
        return self


@component("tagger", assigns=["token.tag", "token.pos", "token.lemma"], default_model=default_tagger)
class Tagger(Pipe):
    """Pipeline component for part-of-speech tagging.

    DOCS: https://spacy.io/api/tagger
    """

    def __init__(self, vocab, model, **cfg):
        self.vocab = vocab
        self.model = model
        self._rehearsal_model = None
        self.cfg = dict(sorted(cfg.items()))

    @property
    def labels(self):
        return tuple(self.vocab.morphology.tag_names)

    def __call__(self, doc):
        tags = self.predict([doc])
        self.set_annotations([doc], tags)
        return doc

    def pipe(self, stream, batch_size=128):
        for docs in util.minibatch(stream, size=batch_size):
            tag_ids = self.predict(docs)
            self.set_annotations(docs, tag_ids)
            yield from docs

    def predict(self, docs):
        if not any(len(doc) for doc in docs):
            # Handle cases where there are no tokens in any docs.
            n_labels = len(self.labels)
            guesses = [self.model.ops.alloc((0, n_labels)) for doc in docs]
            assert len(guesses) == len(docs)
            return guesses
        scores = self.model.predict(docs)
        assert len(scores) == len(docs), (len(scores), len(docs))
        guesses = self._scores2guesses(scores)
        assert len(guesses) == len(docs)
        return guesses

    def _scores2guesses(self, scores):
        guesses = []
        for doc_scores in scores:
            doc_guesses = doc_scores.argmax(axis=1)
            if not isinstance(doc_guesses, numpy.ndarray):
                doc_guesses = doc_guesses.get()
            guesses.append(doc_guesses)
        return guesses

    def set_annotations(self, docs, batch_tag_ids):
        if isinstance(docs, Doc):
            docs = [docs]
        cdef Doc doc
        cdef int idx = 0
        cdef Vocab vocab = self.vocab
        assign_morphology = self.cfg.get("set_morphology", True)
        for i, doc in enumerate(docs):
            doc_tag_ids = batch_tag_ids[i]
            if hasattr(doc_tag_ids, "get"):
                doc_tag_ids = doc_tag_ids.get()
            for j, tag_id in enumerate(doc_tag_ids):
                # Don't clobber preset POS tags
                if doc.c[j].tag == 0:
                    if doc.c[j].pos == 0 and assign_morphology:
                        # Don't clobber preset lemmas
                        lemma = doc.c[j].lemma
                        vocab.morphology.assign_tag_id(&doc.c[j], tag_id)
                        if lemma != 0 and lemma != doc.c[j].lex.orth:
                            doc.c[j].lemma = lemma
                    else:
                        doc.c[j].tag = self.vocab.strings[self.labels[tag_id]]
                idx += 1
            doc.is_tagged = True

    def update(self, examples, *, drop=0., sgd=None, losses=None, set_annotations=False):
        if losses is None:
            losses = {}
        losses.setdefault(self.name, 0.0)

        try:
            if not any(len(eg.predicted) if eg.predicted else 0 for eg in examples):
                # Handle cases where there are no tokens in any docs.
                return
        except AttributeError:
            types = set([type(eg) for eg in examples])
            raise TypeError(Errors.E978.format(name="Tagger", method="update", types=types))
        set_dropout_rate(self.model, drop)
        tag_scores, bp_tag_scores = self.model.begin_update(
            [eg.predicted for eg in examples])
        for sc in tag_scores:
            if self.model.ops.xp.isnan(sc.sum()):
                raise ValueError("nan value in scores")
        loss, d_tag_scores = self.get_loss(examples, tag_scores)
        bp_tag_scores(d_tag_scores)
        if sgd not in (None, False):
            self.model.finish_update(sgd)

        losses[self.name] += loss
        if set_annotations:
            docs = [eg.predicted for eg in examples]
            self.set_annotations(docs, self._scores2guesses(tag_scores))
        return losses

    def rehearse(self, examples, drop=0., sgd=None, losses=None):
        """Perform a 'rehearsal' update, where we try to match the output of
        an initial model.
        """
        try:
            docs = [eg.predicted for eg in examples]
        except AttributeError:
            types = set([type(eg) for eg in examples])
            raise TypeError(Errors.E978.format(name="Tagger", method="rehearse", types=types))
        if self._rehearsal_model is None:
            return
        if not any(len(doc) for doc in docs):
            # Handle cases where there are no tokens in any docs.
            return
        set_dropout_rate(self.model, drop)
        guesses, backprop = self.model.begin_update(docs)
        target = self._rehearsal_model(examples)
        gradient = guesses - target
        backprop(gradient)
        self.model.finish_update(sgd)
        if losses is not None:
            losses.setdefault(self.name, 0.0)
            losses[self.name] += (gradient**2).sum()

    def get_loss(self, examples, scores):
        loss_func = SequenceCategoricalCrossentropy(names=self.labels, normalize=False)
        truths = [eg.get_aligned("tag", as_string=True) for eg in examples]
        d_scores, loss = loss_func(scores, truths)
        if self.model.ops.xp.isnan(loss):
            raise ValueError("nan value when computing loss")
        return float(loss), d_scores

    def begin_training(self, get_examples=lambda: [], pipeline=None, sgd=None,
                       **kwargs):
        lemma_tables = ["lemma_rules", "lemma_index", "lemma_exc", "lemma_lookup"]
        if not any(table in self.vocab.lookups for table in lemma_tables):
            warnings.warn(Warnings.W022)
        if len(self.vocab.lookups.get_table("lexeme_norm", {})) == 0:
            warnings.warn(Warnings.W033.format(model="part-of-speech tagger"))
        orig_tag_map = dict(self.vocab.morphology.tag_map)
        new_tag_map = {}
        for example in get_examples():
            try:
                y = example.y
            except AttributeError:
                raise TypeError(Errors.E978.format(name="Tagger", method="begin_training", types=type(example)))
            for token in y:
                tag = token.tag_
                if tag in orig_tag_map:
                    new_tag_map[tag] = orig_tag_map[tag]
                else:
                    new_tag_map[tag] = {POS: X}

        cdef Vocab vocab = self.vocab
        if new_tag_map:
            if "_SP" in orig_tag_map:
                new_tag_map["_SP"] = orig_tag_map["_SP"]
            vocab.morphology = Morphology(vocab.strings, new_tag_map,
                                          vocab.morphology.lemmatizer,
                                          exc=vocab.morphology.exc)
        self.set_output(len(self.labels))
        doc_sample = [Doc(self.vocab, words=["hello", "world"])]
        if pipeline is not None:
            for name, component in pipeline:
                if component is self:
                    break
                if hasattr(component, "pipe"):
                    doc_sample = list(component.pipe(doc_sample))
                else:
                    doc_sample = [component(doc) for doc in doc_sample]
        self.model.initialize(X=doc_sample)
        # Get batch of example docs, example outputs to call begin_training().
        # This lets the model infer shapes.
        link_vectors_to_models(self.vocab)
        if sgd is None:
            sgd = self.create_optimizer()
        return sgd

    def add_label(self, label, values=None):
        if not isinstance(label, str):
            raise ValueError(Errors.E187)
        if label in self.labels:
            return 0
        if self.model.has_dim("nO"):
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

    def to_bytes(self, exclude=tuple()):
        serialize = {}
        serialize["model"] = self.model.to_bytes
        serialize["vocab"] = self.vocab.to_bytes
        serialize["cfg"] = lambda: srsly.json_dumps(self.cfg)
        tag_map = dict(sorted(self.vocab.morphology.tag_map.items()))
        serialize["tag_map"] = lambda: srsly.msgpack_dumps(tag_map)
        return util.to_bytes(serialize, exclude)

    def from_bytes(self, bytes_data, exclude=tuple()):
        def load_model(b):
            try:
                self.model.from_bytes(b)
            except AttributeError:
                raise ValueError(Errors.E149)

        def load_tag_map(b):
            tag_map = srsly.msgpack_loads(b)
            self.vocab.morphology = Morphology(
                self.vocab.strings, tag_map=tag_map,
                lemmatizer=self.vocab.morphology.lemmatizer,
                exc=self.vocab.morphology.exc)

        deserialize = {
            "vocab": lambda b: self.vocab.from_bytes(b),
            "tag_map": load_tag_map,
            "cfg": lambda b: self.cfg.update(srsly.json_loads(b)),
            "model": lambda b: load_model(b),
        }
        util.from_bytes(bytes_data, deserialize, exclude)
        return self

    def to_disk(self, path, exclude=tuple()):
        tag_map = dict(sorted(self.vocab.morphology.tag_map.items()))
        serialize = {
            "vocab": lambda p: self.vocab.to_disk(p),
            "tag_map": lambda p: srsly.write_msgpack(p, tag_map),
            "model": lambda p: self.model.to_disk(p),
            "cfg": lambda p: srsly.write_json(p, self.cfg),
        }
        util.to_disk(path, serialize, exclude)

    def from_disk(self, path, exclude=tuple()):
        def load_model(p):
            with p.open("rb") as file_:
                try:
                    self.model.from_bytes(file_.read())
                except AttributeError:
                    raise ValueError(Errors.E149)

        def load_tag_map(p):
            tag_map = srsly.read_msgpack(p)
            self.vocab.morphology = Morphology(
                self.vocab.strings, tag_map=tag_map,
                lemmatizer=self.vocab.morphology.lemmatizer,
                exc=self.vocab.morphology.exc)

        deserialize = {
            "vocab": lambda p: self.vocab.from_disk(p),
            "cfg": lambda p: self.cfg.update(_load_cfg(p)),
            "tag_map": load_tag_map,
            "model": load_model,
        }
        util.from_disk(path, deserialize, exclude)
        return self


@component("senter", assigns=["token.is_sent_start"], default_model=default_senter)
class SentenceRecognizer(Tagger):
    """Pipeline component for sentence segmentation.

    DOCS: https://spacy.io/api/sentencerecognizer
    """

    def __init__(self, vocab, model, **cfg):
        self.vocab = vocab
        self.model = model
        self._rehearsal_model = None
        self.cfg = dict(sorted(cfg.items()))

    @property
    def labels(self):
        # labels are numbered by index internally, so this matches GoldParse
        # and Example where the sentence-initial tag is 1 and other positions
        # are 0
        return tuple(["I", "S"])

    def set_annotations(self, docs, batch_tag_ids):
        if isinstance(docs, Doc):
            docs = [docs]
        cdef Doc doc
        for i, doc in enumerate(docs):
            doc_tag_ids = batch_tag_ids[i]
            if hasattr(doc_tag_ids, "get"):
                doc_tag_ids = doc_tag_ids.get()
            for j, tag_id in enumerate(doc_tag_ids):
                # Don't clobber existing sentence boundaries
                if doc.c[j].sent_start == 0:
                    if tag_id == 1:
                        doc.c[j].sent_start = 1
                    else:
                        doc.c[j].sent_start = -1

    def get_loss(self, examples, scores):
        labels = self.labels
        loss_func = SequenceCategoricalCrossentropy(names=labels, normalize=False)
        truths = []
        for eg in examples:
            eg_truth = []
            for x in eg.get_aligned("sent_start"):
                if x == None:
                    eg_truth.append(None)
                elif x == 1:
                    eg_truth.append(labels[1])
                else:
                    # anything other than 1: 0, -1, -1 as uint64
                    eg_truth.append(labels[0])
            truths.append(eg_truth)
        d_scores, loss = loss_func(scores, truths)
        if self.model.ops.xp.isnan(loss):
            raise ValueError("nan value when computing loss")
        return float(loss), d_scores

    def begin_training(self, get_examples=lambda: [], pipeline=None, sgd=None,
                       **kwargs):
        self.set_output(len(self.labels))
        self.model.initialize()
        link_vectors_to_models(self.vocab)
        if sgd is None:
            sgd = self.create_optimizer()
        return sgd

    def add_label(self, label, values=None):
        raise NotImplementedError

    def to_bytes(self, exclude=tuple()):
        serialize = {}
        serialize["model"] = self.model.to_bytes
        serialize["vocab"] = self.vocab.to_bytes
        serialize["cfg"] = lambda: srsly.json_dumps(self.cfg)
        return util.to_bytes(serialize, exclude)

    def from_bytes(self, bytes_data, exclude=tuple()):
        def load_model(b):
            try:
                self.model.from_bytes(b)
            except AttributeError:
                raise ValueError(Errors.E149)

        deserialize = {
            "vocab": lambda b: self.vocab.from_bytes(b),
            "cfg": lambda b: self.cfg.update(srsly.json_loads(b)),
            "model": lambda b: load_model(b),
        }
        util.from_bytes(bytes_data, deserialize, exclude)
        return self

    def to_disk(self, path, exclude=tuple()):
        serialize = {
            "vocab": lambda p: self.vocab.to_disk(p),
            "model": lambda p: p.open("wb").write(self.model.to_bytes()),
            "cfg": lambda p: srsly.write_json(p, self.cfg),
        }
        util.to_disk(path, serialize, exclude)

    def from_disk(self, path, exclude=tuple()):
        def load_model(p):
            with p.open("rb") as file_:
                try:
                    self.model.from_bytes(file_.read())
                except AttributeError:
                    raise ValueError(Errors.E149)

        deserialize = {
            "vocab": lambda p: self.vocab.from_disk(p),
            "cfg": lambda p: self.cfg.update(_load_cfg(p)),
            "model": load_model,
        }
        util.from_disk(path, deserialize, exclude)
        return self


@component("nn_labeller")
class MultitaskObjective(Tagger):
    """Experimental: Assist training of a parser or tagger, by training a
    side-objective.
    """

    def __init__(self, vocab, model, **cfg):
        self.vocab = vocab
        self.model = model
        target = cfg["target"]   # default: 'dep_tag_offset'
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

    @property
    def labels(self):
        return self.cfg.setdefault("labels", {})

    @labels.setter
    def labels(self, value):
        self.cfg["labels"] = value

    def set_annotations(self, docs, dep_ids):
        pass

    def begin_training(self, get_examples=lambda: [], pipeline=None,
                       sgd=None, **kwargs):
        gold_examples = nonproj.preprocess_training_data(get_examples())
        # for raw_text, doc_annot in gold_tuples:
        for example in gold_examples:
            for token in example.y:
                label = self.make_label(token)
                if label is not None and label not in self.labels:
                    self.labels[label] = len(self.labels)
        self.model.initialize()
        link_vectors_to_models(self.vocab)
        if sgd is None:
            sgd = self.create_optimizer()
        return sgd

    def predict(self, docs):
        tokvecs = self.model.get_ref("tok2vec")(docs)
        scores = self.model.get_ref("softmax")(tokvecs)
        return tokvecs, scores

    def get_loss(self, examples, scores):
        cdef int idx = 0
        correct = numpy.zeros((scores.shape[0],), dtype="i")
        guesses = scores.argmax(axis=1)
        docs = [eg.predicted for eg in examples]
        for i, eg in enumerate(examples):
            # Handles alignment for tokenization differences
            doc_annots = eg.get_aligned()  # TODO
            for j in range(len(eg.predicted)):
                tok_annots = {key: values[j] for key, values in tok_annots.items()}
                label = self.make_label(j, tok_annots)
                if label is None or label not in self.labels:
                    correct[idx] = guesses[idx]
                else:
                    correct[idx] = self.labels[label]
                idx += 1
        correct = self.model.ops.xp.array(correct, dtype="i")
        d_scores = scores - to_categorical(correct, n_classes=scores.shape[1])
        loss = (d_scores**2).sum()
        return float(loss), d_scores

    @staticmethod
    def make_dep(token):
        return token.dep_

    @staticmethod
    def make_tag(token):
        return token.tag_

    @staticmethod
    def make_ent(token):
        if token.ent_iob_ == "O":
            return "O"
        else:
            return token.ent_iob_ + "-" + token.ent_type_

    @staticmethod
    def make_dep_tag_offset(token):
        dep = token.dep_
        tag = token.tag_
        offset = token.head.i - token.i
        offset = min(offset, 2)
        offset = max(offset, -2)
        return f"{dep}-{tag}:{offset}"

    @staticmethod
    def make_ent_tag(token):
        if token.ent_iob_ == "O":
            ent = "O"
        else:
            ent = token.ent_iob_ + "-" + token.ent_type_
        tag = token.tag_
        return f"{tag}-{ent}"

    @staticmethod
    def make_sent_start(token):
        """A multi-task objective for representing sentence boundaries,
        using BILU scheme. (O is impossible)
        """
        if token.is_sent_start and token.is_sent_end:
            return "U-SENT"
        elif token.is_sent_start:
            return "B-SENT"
        else:
            return "I-SENT"


class ClozeMultitask(Pipe):
    def __init__(self, vocab, model, **cfg):
        self.vocab = vocab
        self.model = model
        self.cfg = cfg
        self.distance = CosineDistance(ignore_zeros=True, normalize=False)  # TODO: in config

    def set_annotations(self, docs, dep_ids):
        pass

    def begin_training(self, get_examples=lambda: [], pipeline=None,
                       sgd=None, **kwargs):
        link_vectors_to_models(self.vocab)
        self.model.initialize()
        X = self.model.ops.alloc((5, self.model.get_ref("tok2vec").get_dim("nO")))
        self.model.output_layer.begin_training(X)
        if sgd is None:
            sgd = self.create_optimizer()
        return sgd

    def predict(self, docs):
        tokvecs = self.model.get_ref("tok2vec")(docs)
        vectors = self.model.get_ref("output_layer")(tokvecs)
        return tokvecs, vectors

    def get_loss(self, examples, vectors, prediction):
        # The simplest way to implement this would be to vstack the
        # token.vector values, but that's a bit inefficient, especially on GPU.
        # Instead we fetch the index into the vectors table for each of our tokens,
        # and look them up all at once. This prevents data copying.
        ids = self.model.ops.flatten([eg.predicted.to_array(ID).ravel() for eg in examples])
        target = vectors[ids]
        gradient = self.distance.get_grad(prediction, target)
        loss = self.distance.get_loss(prediction, target)
        return loss, gradient

    def update(self, examples, *, drop=0., set_annotations=False, sgd=None, losses=None):
        pass

    def rehearse(self, examples, drop=0., sgd=None, losses=None):
        if losses is not None and self.name not in losses:
            losses[self.name] = 0.
        set_dropout_rate(self.model, drop)
        try:
            predictions, bp_predictions = self.model.begin_update([eg.predicted for eg in examples])
        except AttributeError:
            types = set([type(eg) for eg in examples])
            raise TypeError(Errors.E978.format(name="ClozeMultitask", method="rehearse", types=types))
        loss, d_predictions = self.get_loss(examples, self.vocab.vectors.data, predictions)
        bp_predictions(d_predictions)
        if sgd is not None:
            self.model.finish_update(sgd)

        if losses is not None:
            losses[self.name] += loss


@component("textcat", assigns=["doc.cats"], default_model=default_textcat)
class TextCategorizer(Pipe):
    """Pipeline component for text classification.

    DOCS: https://spacy.io/api/textcategorizer
    """
    def __init__(self, vocab, model, **cfg):
        self.vocab = vocab
        self.model = model
        self._rehearsal_model = None
        self.cfg = dict(cfg)

    @property
    def labels(self):
        return tuple(self.cfg.setdefault("labels", []))

    def require_labels(self):
        """Raise an error if the component's model has no labels defined."""
        if not self.labels:
            raise ValueError(Errors.E143.format(name=self.name))

    @labels.setter
    def labels(self, value):
        self.cfg["labels"] = tuple(value)

    def pipe(self, stream, batch_size=128):
        for docs in util.minibatch(stream, size=batch_size):
            scores = self.predict(docs)
            self.set_annotations(docs, scores)
            yield from docs

    def predict(self, docs):
        tensors = [doc.tensor for doc in docs]

        if not any(len(doc) for doc in docs):
            # Handle cases where there are no tokens in any docs.
            xp = get_array_module(tensors)
            scores = xp.zeros((len(docs), len(self.labels)))
            return scores

        scores = self.model.predict(docs)
        scores = self.model.ops.asarray(scores)
        return scores

    def set_annotations(self, docs, scores):
        for i, doc in enumerate(docs):
            for j, label in enumerate(self.labels):
                doc.cats[label] = float(scores[i, j])

    def update(self, examples, *, drop=0., set_annotations=False, sgd=None, losses=None):
        if losses is None:
            losses = {}
        losses.setdefault(self.name, 0.0)
        try:
            if not any(len(eg.predicted) if eg.predicted else 0 for eg in examples):
                # Handle cases where there are no tokens in any docs.
                return losses
        except AttributeError:
            types = set([type(eg) for eg in examples])
            raise TypeError(Errors.E978.format(name="TextCategorizer", method="update", types=types))
        set_dropout_rate(self.model, drop)
        scores, bp_scores = self.model.begin_update(
            [eg.predicted for eg in examples]
        )
        loss, d_scores = self.get_loss(examples, scores)
        bp_scores(d_scores)
        if sgd is not None:
            self.model.finish_update(sgd)
        losses[self.name] += loss
        if set_annotations:
            docs = [eg.predicted for eg in examples]
            self.set_annotations(docs, scores=scores)
        return losses

    def rehearse(self, examples, drop=0., sgd=None, losses=None):
        if self._rehearsal_model is None:
            return
        try:
            docs = [eg.predicted for eg in examples]
        except AttributeError:
            types = set([type(eg) for eg in examples])
            raise TypeError(Errors.E978.format(name="TextCategorizer", method="rehearse", types=types))
        if not any(len(doc) for doc in docs):
            # Handle cases where there are no tokens in any docs.
            return
        set_dropout_rate(self.model, drop)
        scores, bp_scores = self.model.begin_update(docs)
        target = self._rehearsal_model(examples)
        gradient = scores - target
        bp_scores(gradient)
        if sgd is not None:
            self.model.finish_update(sgd)
        if losses is not None:
            losses.setdefault(self.name, 0.0)
            losses[self.name] += (gradient**2).sum()

    def _examples_to_truth(self, examples):
        truths = numpy.zeros((len(examples), len(self.labels)), dtype="f")
        not_missing = numpy.ones((len(examples), len(self.labels)), dtype="f")
        for i, eg in enumerate(examples):
            for j, label in enumerate(self.labels):
                if label in eg.reference.cats:
                    truths[i, j] = eg.reference.cats[label]
                else:
                    not_missing[i, j] = 0.
        truths = self.model.ops.asarray(truths)
        return truths, not_missing

    def get_loss(self, examples, scores):
        truths, not_missing = self._examples_to_truth(examples)
        not_missing = self.model.ops.asarray(not_missing)
        d_scores = (scores-truths) / scores.shape[0]
        d_scores *= not_missing
        mean_square_error = (d_scores**2).sum(axis=1).mean()
        return float(mean_square_error), d_scores

    def add_label(self, label):
        if not isinstance(label, str):
            raise ValueError(Errors.E187)
        if label in self.labels:
            return 0
        if self.model.has_dim("nO"):
            # This functionality was available previously, but was broken.
            # The problem is that we resize the last layer, but the last layer
            # is actually just an ensemble. We're not resizing the child layers
            # - a huge problem.
            raise ValueError(Errors.E116)
            # smaller = self.model._layers[-1]
            # larger = Linear(len(self.labels)+1, smaller.nI)
            # copy_array(larger.W[:smaller.nO], smaller.W)
            # copy_array(larger.b[:smaller.nO], smaller.b)
            # self.model._layers[-1] = larger
        self.labels = tuple(list(self.labels) + [label])
        return 1

    def begin_training(self, get_examples=lambda: [], pipeline=None, sgd=None, **kwargs):
        # TODO: begin_training is not guaranteed to see all data / labels ?
        examples = list(get_examples())
        for example in examples:
            try:
                y = example.y
            except AttributeError:
                raise TypeError(Errors.E978.format(name="TextCategorizer", method="update", types=type(example)))
            for cat in y.cats:
                self.add_label(cat)
        self.require_labels()
        docs = [Doc(Vocab(), words=["hello"])]
        truths, _ = self._examples_to_truth(examples)
        self.set_output(len(self.labels))
        link_vectors_to_models(self.vocab)
        self.model.initialize(X=docs, Y=truths)
        if sgd is None:
            sgd = self.create_optimizer()
        return sgd


cdef class DependencyParser(Parser):
    """Pipeline component for dependency parsing.

    DOCS: https://spacy.io/api/dependencyparser
    """
    # cdef classes can't have decorators, so we're defining this here
    name = "parser"
    factory = "parser"
    assigns = ["token.dep", "token.is_sent_start", "doc.sents"]
    requires = []
    TransitionSystem = ArcEager

    @property
    def postprocesses(self):
        output = [nonproj.deprojectivize]
        if self.cfg.get("learn_tokens") is True:
            output.append(merge_subtokens)
        return tuple(output)

    def add_multitask_objective(self, mt_component):
        self._multitasks.append(mt_component)

    def init_multitask_objectives(self, get_examples, pipeline, sgd=None, **cfg):
        # TODO: transfer self.model.get_ref("tok2vec") to the multitask's model ?
        for labeller in self._multitasks:
            labeller.model.set_dim("nO", len(self.labels))
            if labeller.model.has_ref("output_layer"):
                labeller.model.get_ref("output_layer").set_dim("nO", len(self.labels))
            labeller.begin_training(get_examples, pipeline=pipeline, sgd=sgd)

    def __reduce__(self):
        return (DependencyParser, (self.vocab, self.model), (self.moves, self.cfg))

    def __getstate__(self):
        return (self.moves, self.cfg)

    def __setstate__(self, state):
        moves, config = state
        self.moves = moves
        self.cfg = config

    @property
    def labels(self):
        labels = set()
        # Get the labels from the model by looking at the available moves
        for move in self.move_names:
            if "-" in move:
                label = move.split("-")[1]
                if "||" in label:
                    label = label.split("||")[1]
                labels.add(label)
        return tuple(sorted(labels))


cdef class EntityRecognizer(Parser):
    """Pipeline component for named entity recognition.

    DOCS: https://spacy.io/api/entityrecognizer
    """
    name = "ner"
    factory = "ner"
    assigns = ["doc.ents", "token.ent_iob", "token.ent_type"]
    requires = []
    TransitionSystem = BiluoPushDown

    def add_multitask_objective(self, mt_component):
        self._multitasks.append(mt_component)

    def init_multitask_objectives(self, get_examples, pipeline, sgd=None, **cfg):
        # TODO: transfer self.model.get_ref("tok2vec") to the multitask's model ?
        for labeller in self._multitasks:
            labeller.model.set_dim("nO", len(self.labels))
            if labeller.model.has_ref("output_layer"):
                labeller.model.get_ref("output_layer").set_dim("nO", len(self.labels))
            labeller.begin_training(get_examples, pipeline=pipeline)

    def __reduce__(self):
        return (EntityRecognizer, (self.vocab, self.model), (self.moves, self.cfg))

    def __getstate__(self):
        return self.moves, self.cfg

    def __setstate__(self, state):
        moves, config = state
        self.moves = moves
        self.cfg = config

    @property
    def labels(self):
        # Get the labels from the model by looking at the available moves, e.g.
        # B-PERSON, I-PERSON, L-PERSON, U-PERSON
        labels = set(move.split("-")[1] for move in self.move_names
                     if move[0] in ("B", "I", "L", "U"))
        return tuple(sorted(labels))


@component(
    "entity_linker",
    requires=["doc.ents", "doc.sents", "token.ent_iob", "token.ent_type"],
    assigns=["token.ent_kb_id"],
    default_model=default_nel,
)
class EntityLinker(Pipe):
    """Pipeline component for named entity linking.

    DOCS: https://spacy.io/api/entitylinker
    """
    NIL = "NIL"  # string used to refer to a non-existing link

    def __init__(self, vocab, model, **cfg):
        self.vocab = vocab
        self.model = model
        self.kb = None
        self.kb = cfg.get("kb", None)
        if self.kb is None:
            # create an empty KB that should be filled by calling from_disk
            self.kb = KnowledgeBase(vocab=vocab)
        else:
            del cfg["kb"]   # we don't want to duplicate its serialization
        if not isinstance(self.kb, KnowledgeBase):
            raise ValueError(Errors.E990.format(type=type(self.kb)))
        self.cfg = dict(cfg)
        self.distance = CosineDistance(normalize=False)
        # how many neightbour sentences to take into account
        self.n_sents = cfg.get("n_sents", 0)

    def require_kb(self):
        # Raise an error if the knowledge base is not initialized.
        if len(self.kb) == 0:
            raise ValueError(Errors.E139.format(name=self.name))

    def begin_training(self, get_examples=lambda: [], pipeline=None, sgd=None, **kwargs):
        self.require_kb()
        nO = self.kb.entity_vector_length
        self.set_output(nO)
        self.model.initialize()
        if sgd is None:
            sgd = self.create_optimizer()
        return sgd

    def update(self, examples, *, set_annotations=False, drop=0.0, sgd=None, losses=None):
        self.require_kb()
        if losses is None:
            losses = {}
        losses.setdefault(self.name, 0.0)
        if not examples:
            return losses
        sentence_docs = []
        try:
            docs = [eg.predicted for eg in examples]
        except AttributeError:
            types = set([type(eg) for eg in examples])
            raise TypeError(Errors.E978.format(name="EntityLinker", method="update", types=types))
        if set_annotations:
            # This seems simpler than other ways to get that exact output -- but
            # it does run the model twice :(
            predictions = self.model.predict(docs)

        for eg in examples:
            sentences = [s for s in eg.predicted.sents]
            kb_ids = eg.get_aligned("ENT_KB_ID", as_string=True)
            for ent in eg.predicted.ents:
                kb_id = kb_ids[ent.start]  # KB ID of the first token is the same as the whole span
                if kb_id:
                    try:
                        # find the sentence in the list of sentences.
                        sent_index = sentences.index(ent.sent)
                    except AttributeError:
                        # Catch the exception when ent.sent is None and provide a user-friendly warning
                        raise RuntimeError(Errors.E030)
                    # get n previous sentences, if there are any
                    start_sentence = max(0, sent_index - self.n_sents)

                    # get n posterior sentences, or as many < n as there are
                    end_sentence = min(len(sentences) -1, sent_index + self.n_sents)

                    # get token positions
                    start_token = sentences[start_sentence].start
                    end_token = sentences[end_sentence].end

                    # append that span as a doc to training
                    sent_doc = eg.predicted[start_token:end_token].as_doc()
                    sentence_docs.append(sent_doc)
        set_dropout_rate(self.model, drop)
        if not sentence_docs:
            warnings.warn(Warnings.W093.format(name="Entity Linker"))
            return 0.0
        sentence_encodings, bp_context = self.model.begin_update(sentence_docs)
        loss, d_scores = self.get_similarity_loss(
            sentence_encodings=sentence_encodings,
            examples=examples
        )
        bp_context(d_scores)
        if sgd is not None:
            self.model.finish_update(sgd)

        losses[self.name] += loss
        if set_annotations:
            self.set_annotations(docs, predictions)
        return losses

    def get_similarity_loss(self, examples, sentence_encodings):
        entity_encodings = []
        for eg in examples:
            kb_ids = eg.get_aligned("ENT_KB_ID", as_string=True)
            for ent in eg.predicted.ents:
                kb_id = kb_ids[ent.start]
                if kb_id:
                    entity_encoding = self.kb.get_vector(kb_id)
                    entity_encodings.append(entity_encoding)

        entity_encodings = self.model.ops.asarray(entity_encodings, dtype="float32")

        if sentence_encodings.shape != entity_encodings.shape:
            raise RuntimeError(Errors.E147.format(method="get_similarity_loss", msg="gold entities do not match up"))

        gradients = self.distance.get_grad(sentence_encodings, entity_encodings)
        loss = self.distance.get_loss(sentence_encodings, entity_encodings)
        loss = loss / len(entity_encodings)
        return loss, gradients

    def __call__(self, doc):
        kb_ids = self.predict([doc])
        self.set_annotations([doc], kb_ids)
        return doc

    def pipe(self, stream, batch_size=128):
        for docs in util.minibatch(stream, size=batch_size):
            kb_ids = self.predict(docs)
            self.set_annotations(docs, kb_ids)
            yield from docs

    def predict(self, docs):
        """ Return the KB IDs for each entity in each doc, including NIL if there is no prediction """
        self.require_kb()
        entity_count = 0
        final_kb_ids = []

        if not docs:
            return final_kb_ids

        if isinstance(docs, Doc):
            docs = [docs]

        for i, doc in enumerate(docs):
            sentences = [s for s in doc.sents]

            if len(doc) > 0:
                # Looping through each sentence and each entity
                # This may go wrong if there are entities across sentences - which shouldn't happen normally.
                for sent_index, sent in enumerate(sentences):
                    if sent.ents:
                        # get n_neightbour sentences, clipped to the length of the document
                        start_sentence = max(0, sent_index - self.n_sents)
                        end_sentence = min(len(sentences) -1, sent_index + self.n_sents)

                        start_token = sentences[start_sentence].start
                        end_token = sentences[end_sentence].end

                        sent_doc = doc[start_token:end_token].as_doc()
                        # currently, the context is the same for each entity in a sentence (should be refined)
                        sentence_encoding = self.model.predict([sent_doc])[0]
                        xp = get_array_module(sentence_encoding)
                        sentence_encoding_t = sentence_encoding.T
                        sentence_norm = xp.linalg.norm(sentence_encoding_t)

                        for ent in sent.ents:
                            entity_count += 1

                            to_discard = self.cfg.get("labels_discard", [])
                            if to_discard and ent.label_ in to_discard:
                                # ignoring this entity - setting to NIL
                                final_kb_ids.append(self.NIL)

                            else:
                                candidates = self.kb.get_candidates(ent.text)
                                if not candidates:
                                    # no prediction possible for this entity - setting to NIL
                                    final_kb_ids.append(self.NIL)

                                elif len(candidates) == 1:
                                    # shortcut for efficiency reasons: take the 1 candidate

                                    # TODO: thresholding
                                    final_kb_ids.append(candidates[0].entity_)

                                else:
                                    random.shuffle(candidates)

                                    # this will set all prior probabilities to 0 if they should be excluded from the model
                                    prior_probs = xp.asarray([c.prior_prob for c in candidates])
                                    if not self.cfg.get("incl_prior", True):
                                        prior_probs = xp.asarray([0.0 for c in candidates])
                                    scores = prior_probs

                                    # add in similarity from the context
                                    if self.cfg.get("incl_context", True):
                                        entity_encodings = xp.asarray([c.entity_vector for c in candidates])
                                        entity_norm = xp.linalg.norm(entity_encodings, axis=1)

                                        if len(entity_encodings) != len(prior_probs):
                                            raise RuntimeError(Errors.E147.format(method="predict", msg="vectors not of equal length"))

                                        # cosine similarity
                                        sims = xp.dot(entity_encodings, sentence_encoding_t) / (sentence_norm * entity_norm)
                                        if sims.shape != prior_probs.shape:
                                            raise ValueError(Errors.E161)
                                        scores = prior_probs + sims - (prior_probs*sims)

                                    # TODO: thresholding
                                    best_index = scores.argmax().item()
                                    best_candidate = candidates[best_index]
                                    final_kb_ids.append(best_candidate.entity_)

        if not (len(final_kb_ids) == entity_count):
            raise RuntimeError(Errors.E147.format(method="predict", msg="result variables not of equal length"))

        return final_kb_ids

    def set_annotations(self, docs, kb_ids):
        count_ents = len([ent for doc in docs for ent in doc.ents])
        if count_ents != len(kb_ids):
            raise ValueError(Errors.E148.format(ents=count_ents, ids=len(kb_ids)))

        i=0
        for doc in docs:
            for ent in doc.ents:
                kb_id = kb_ids[i]
                i += 1
                for token in ent:
                    token.ent_kb_id_ = kb_id

    def to_disk(self, path, exclude=tuple()):
        serialize = {}
        self.cfg["entity_width"] = self.kb.entity_vector_length
        serialize["cfg"] = lambda p: srsly.write_json(p, self.cfg)
        serialize["vocab"] = lambda p: self.vocab.to_disk(p)
        serialize["kb"] = lambda p: self.kb.dump(p)
        serialize["model"] = lambda p: self.model.to_disk(p)
        util.to_disk(path, serialize, exclude)

    def from_disk(self, path, exclude=tuple()):
        def load_model(p):
            try:
                self.model.from_bytes(p.open("rb").read())
            except AttributeError:
                raise ValueError(Errors.E149)

        def load_kb(p):
            self.kb = KnowledgeBase(vocab=self.vocab, entity_vector_length=self.cfg["entity_width"])
            self.kb.load_bulk(p)

        deserialize = {}
        deserialize["vocab"] = lambda p: self.vocab.from_disk(p)
        deserialize["cfg"] = lambda p: self.cfg.update(_load_cfg(p))
        deserialize["kb"] = load_kb
        deserialize["model"] = load_model
        util.from_disk(path, deserialize, exclude)
        return self

    def rehearse(self, examples, sgd=None, losses=None, **config):
        raise NotImplementedError

    def add_label(self, label):
        raise NotImplementedError


@component("sentencizer", assigns=["token.is_sent_start", "doc.sents"])
class Sentencizer(Pipe):
    """Segment the Doc into sentences using a rule-based strategy.

    DOCS: https://spacy.io/api/sentencizer
    """

    default_punct_chars = ['!', '.', '?', '։', '؟', '۔', '܀', '܁', '܂', '߹',
            '।', '॥', '၊', '။', '።', '፧', '፨', '᙮', '᜵', '᜶', '᠃', '᠉', '᥄',
            '᥅', '᪨', '᪩', '᪪', '᪫', '᭚', '᭛', '᭞', '᭟', '᰻', '᰼', '᱾', '᱿',
            '‼', '‽', '⁇', '⁈', '⁉', '⸮', '⸼', '꓿', '꘎', '꘏', '꛳', '꛷', '꡶',
            '꡷', '꣎', '꣏', '꤯', '꧈', '꧉', '꩝', '꩞', '꩟', '꫰', '꫱', '꯫', '﹒',
            '﹖', '﹗', '！', '．', '？', '𐩖', '𐩗', '𑁇', '𑁈', '𑂾', '𑂿', '𑃀',
            '𑃁', '𑅁', '𑅂', '𑅃', '𑇅', '𑇆', '𑇍', '𑇞', '𑇟', '𑈸', '𑈹', '𑈻', '𑈼',
            '𑊩', '𑑋', '𑑌', '𑗂', '𑗃', '𑗉', '𑗊', '𑗋', '𑗌', '𑗍', '𑗎', '𑗏', '𑗐',
            '𑗑', '𑗒', '𑗓', '𑗔', '𑗕', '𑗖', '𑗗', '𑙁', '𑙂', '𑜼', '𑜽', '𑜾', '𑩂',
            '𑩃', '𑪛', '𑪜', '𑱁', '𑱂', '𖩮', '𖩯', '𖫵', '𖬷', '𖬸', '𖭄', '𛲟', '𝪈',
            '｡', '。']

    def __init__(self, punct_chars=None, **kwargs):
        """Initialize the sentencizer.

        punct_chars (list): Punctuation characters to split on. Will be
            serialized with the nlp object.
        RETURNS (Sentencizer): The sentencizer component.

        DOCS: https://spacy.io/api/sentencizer#init
        """
        if punct_chars:
            self.punct_chars = set(punct_chars)
        else:
            self.punct_chars = set(self.default_punct_chars)

    @classmethod
    def from_nlp(cls, nlp, model=None, **cfg):
        return cls(**cfg)

    def begin_training(
        self, get_examples=lambda: [], pipeline=None, sgd=None, **kwargs
    ):
        pass

    def __call__(self, doc):
        """Apply the sentencizer to a Doc and set Token.is_sent_start.

        example (Doc or Example): The document to process.
        RETURNS (Doc or Example): The processed Doc or Example.

        DOCS: https://spacy.io/api/sentencizer#call
        """
        start = 0
        seen_period = False
        for i, token in enumerate(doc):
            is_in_punct_chars = token.text in self.punct_chars
            token.is_sent_start = i == 0
            if seen_period and not token.is_punct and not is_in_punct_chars:
                doc[start].is_sent_start = True
                start = token.i
                seen_period = False
            elif is_in_punct_chars:
                seen_period = True
        if start < len(doc):
            doc[start].is_sent_start = True
        return doc

    def pipe(self, stream, batch_size=128):
        for docs in util.minibatch(stream, size=batch_size):
            predictions = self.predict(docs)
            self.set_annotations(docs, predictions)
            yield from docs

    def predict(self, docs):
        """Apply the pipeline's model to a batch of docs, without
        modifying them.
        """
        if not any(len(doc) for doc in docs):
            # Handle cases where there are no tokens in any docs.
            guesses = [[] for doc in docs]
            return guesses
        guesses = []
        for doc in docs:
            doc_guesses = [False] * len(doc)
            if len(doc) > 0:
                start = 0
                seen_period = False
                doc_guesses[0] = True
                for i, token in enumerate(doc):
                    is_in_punct_chars = token.text in self.punct_chars
                    if seen_period and not token.is_punct and not is_in_punct_chars:
                        doc_guesses[start] = True
                        start = token.i
                        seen_period = False
                    elif is_in_punct_chars:
                        seen_period = True
                if start < len(doc):
                    doc_guesses[start] = True
            guesses.append(doc_guesses)
        return guesses

    def set_annotations(self, docs, batch_tag_ids):
        if isinstance(docs, Doc):
            docs = [docs]
        cdef Doc doc
        cdef int idx = 0
        for i, doc in enumerate(docs):
            doc_tag_ids = batch_tag_ids[i]
            for j, tag_id in enumerate(doc_tag_ids):
                # Don't clobber existing sentence boundaries
                if doc.c[j].sent_start == 0:
                    if tag_id:
                        doc.c[j].sent_start = 1
                    else:
                        doc.c[j].sent_start = -1

    def to_bytes(self, **kwargs):
        """Serialize the sentencizer to a bytestring.

        RETURNS (bytes): The serialized object.

        DOCS: https://spacy.io/api/sentencizer#to_bytes
        """
        return srsly.msgpack_dumps({"punct_chars": list(self.punct_chars)})

    def from_bytes(self, bytes_data, **kwargs):
        """Load the sentencizer from a bytestring.

        bytes_data (bytes): The data to load.
        returns (Sentencizer): The loaded object.

        DOCS: https://spacy.io/api/sentencizer#from_bytes
        """
        cfg = srsly.msgpack_loads(bytes_data)
        self.punct_chars = set(cfg.get("punct_chars", self.default_punct_chars))
        return self

    def to_disk(self, path, exclude=tuple(), **kwargs):
        """Serialize the sentencizer to disk.

        DOCS: https://spacy.io/api/sentencizer#to_disk
        """
        path = util.ensure_path(path)
        path = path.with_suffix(".json")
        srsly.write_json(path, {"punct_chars": list(self.punct_chars)})


    def from_disk(self, path, exclude=tuple(), **kwargs):
        """Load the sentencizer from disk.

        DOCS: https://spacy.io/api/sentencizer#from_disk
        """
        path = util.ensure_path(path)
        path = path.with_suffix(".json")
        cfg = srsly.read_json(path)
        self.punct_chars = set(cfg.get("punct_chars", self.default_punct_chars))
        return self


# Cython classes can't be decorated, so we need to add the factories here
Language.factories["parser"] = lambda nlp, model, **cfg: parser_factory(nlp, model, **cfg)
Language.factories["ner"] = lambda nlp, model, **cfg: ner_factory(nlp, model, **cfg)

def parser_factory(nlp, model, **cfg):
    default_config = {"learn_tokens": False, "min_action_freq": 30, "beam_width":  1, "beam_update_prob": 1.0}
    if model is None:
        model = default_parser()
        warnings.warn(Warnings.W098.format(name="parser"))
    for key, value in default_config.items():
        if key not in cfg:
            cfg[key] = value
    return DependencyParser.from_nlp(nlp, model, **cfg)

def ner_factory(nlp, model, **cfg):
    default_config = {"learn_tokens": False, "min_action_freq": 30, "beam_width":  1, "beam_update_prob": 1.0}
    if model is None:
        model = default_ner()
        warnings.warn(Warnings.W098.format(name="ner"))
    for key, value in default_config.items():
        if key not in cfg:
            cfg[key] = value
    return EntityRecognizer.from_nlp(nlp, model, **cfg)

__all__ = ["Tagger", "DependencyParser", "EntityRecognizer", "TextCategorizer", "EntityLinker", "Sentencizer", "SentenceRecognizer"]
