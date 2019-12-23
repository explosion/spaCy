# coding: utf8
from __future__ import unicode_literals, division, print_function

from thinc.v2v import Model
from .pipes import Pipe
from ..gold import Example
from ..tokens import Doc
from ..vocab import Vocab
from ..language import component
from .._ml import link_vectors_to_models
from ..util import minibatch, registry, eg2doc


@component("tok2vec", assigns=["doc.tensor"])
class Tok2Vec(Pipe):
    @classmethod
    def from_nlp(cls, nlp, **cfg):
        return cls(nlp.vocab, **cfg)

    @classmethod
    def Model(cls, architecture, **cfg):
        """Create a new statistical model for the class.

        architecture (str): The registered model architecture to use.
        **cfg: Config parameters.
        RETURNS (Model): A `thinc.neural.Model` or similar instance.
        """
        model = registry.architectures.get(architecture)
        return model(**cfg)

    def __init__(self, vocab, model=True, **cfg):
        """Construct a new statistical model. Weights are not allocated on
        initialisation.
        vocab (Vocab): A `Vocab` instance. The model must share the same `Vocab`
            instance with the `Doc` objects it will process.
        model (Model): A `Model` instance or `True` allocate one later.
        **cfg: Config parameters.
        """
        self.vocab = vocab
        self.model = model
        self.cfg = dict(cfg)
        self.listeners = []

    def create_listener(self):
        listener = ControlledModel("tok2vec", {"nO": self.model.nO})
        self.listeners.append(listener)

    def add_listener(self, listener):
        self.listeners.append(listener)

    def find_listeners(self, model):
        for node in model.walk():
            if isinstance(node, ControlledModel) and node.upstream_name == self.name:
                self.add_listener(node)

    def __call__(self, doc):
        """Add context-sensitive vectors to a `Doc`, e.g. from a CNN or LSTM
        model. Vectors are set to the `Doc.tensor` attribute.
        docs (Doc or iterable): One or more documents to add vectors to.
        RETURNS (dict or None): Intermediate computations.
        """
        tokvecses = self.predict([doc])
        self.set_annotations([doc], tokvecses)
        return doc

    def pipe(self, stream, batch_size=128, n_threads=-1, as_example=False):
        """Process `Doc` objects as a stream.
        stream (iterator): A sequence of `Doc` objects to process.
        batch_size (int): Number of `Doc` objects to group.
        n_threads (int): Number of threads.
        YIELDS (iterator): A sequence of `Doc` objects, in order of input.
        """
        for batch in minibatch(stream, batch_size):
            batch = list(batch)
            if as_example:
                docs = [eg2doc(doc) for doc in batch]
            else:
                docs = batch
            tokvecses = self.predict(docs)
            self.set_annotations(docs, tokvecses)
            yield from batch

    def predict(self, docs):
        """Return a single tensor for a batch of documents.
        docs (iterable): A sequence of `Doc` objects.
        RETURNS (object): Vector representations for each token in the documents.
        """
        tokvecs = self.model(docs)
        for listener in self.listeners:
            listener.receive(id(docs), tokvecs, None)
        return tokvecs

    def set_annotations(self, docs, tokvecses):
        """Set the tensor attribute for a batch of documents.
        docs (iterable): A sequence of `Doc` objects.
        tokvecs (object): Vector representation for each token in the documents.
        """
        for doc, tokvecs in zip(docs, tokvecses):
            assert tokvecs.shape[0] == len(doc)
            doc.tensor = tokvecs

    def update(self, examples, drop=0.0, sgd=None, losses=None, set_annotations=False):
        """Update the model.
        examples (iterable): A batch of examples
        drop (float): The droput rate.
        sgd (callable): An optimizer.
        RETURNS (dict): Results from the update.
        """
        if losses is None:
            losses = {}
        examples = Example.to_example_objects(examples)
        docs = [eg.doc for eg in examples]
        if isinstance(docs, Doc):
            docs = [docs]
        tokvecs, bp_tokvecs = self.model.begin_update(docs, drop=drop)
        
        def capture_losses(d_tokvecs, sgd=None):
            """Accumulate tok2vec loss before doing backprop."""
            l2_loss = sum((d_t2v**2).sum() for d_t2v in d_tokvecs)
            if self.name in losses:
                losses[self.name] += l2_loss / len(d_tokvecs)
            else:
                losses[self.name] = l2_loss / len(d_tokvecs)
            return bp_tokvecs(d_tokvecs, sgd=sgd)

        for listener in self.listeners:
            listener.receive(id(docs), tokvecs, capture_losses)
        if set_annotations:
            self.set_annotations(docs, tokvecs)


    def get_loss(self, docs, golds, scores):
        # TODO: implement
        raise NotImplementedError

    def begin_training(self, examples=tuple(), pipeline=None, sgd=None, device=None):
        """Allocate models, pre-process training data and acquire a trainer and
        optimizer.
        gold_tuples (iterable): Gold-standard training data.
        pipeline (list): The pipeline the model is part of.
        """
        if self.model is True:
            self.model = self.Model(**self.cfg)
        docs = [Doc(Vocab(), words=["hello"])]
        self.model.begin_training(docs)
        link_vectors_to_models(self.vocab)


class ControlledModel(Model):
    """A layer that gets fed its answers from an upstream connection,
    for instance from a component earlier in the pipeline.
    """
    name = "dummy-tok2vec"
    def __init__(self, upstream_name, attributes=None):
        Model.__init__(self)
        if attributes is not None:
            for name, value in attributes.items():
                setattr(self, name, value)
        self.upstream_name = upstream_name
        self._batch_id = None
        self._outputs = None
        self._backprop = None

    def receive(self, batch_id, outputs, backprop):
        self._batch_id = batch_id
        self._outputs = outputs
        self._backprop = backprop

    def begin_update(self, inputs, drop=0.):
        self.verify_inputs(inputs)
        return self._outputs, self._backprop

    def verify_inputs(self, inputs):
        if self._batch_id is None and self._outputs is None:
            raise ValueError
        else:
            return True
