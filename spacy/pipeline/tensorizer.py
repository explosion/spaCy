# coding: utf8
from __future__ import unicode_literals

from thinc.v2v import Affine

from .pipe import Pipe
from ..tokens import Doc
from ..errors import Errors
from ..attrs import ID
from .._ml import link_vectors_to_models, zero_init
from .. import util


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
        n_threads (int): Number of threads.
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
                raise ValueError(
                    Errors.E076.format(rows=tensor.shape[0], words=len(doc))
                )
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
