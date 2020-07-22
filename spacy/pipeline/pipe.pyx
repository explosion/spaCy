# cython: infer_types=True, profile=True, binding=True
import srsly

from ..tokens.doc cimport Doc

from ..util import link_vectors_to_models, create_default_optimizer
from ..errors import Errors
from .. import util


def deserialize_config(path):
    if path.exists():
        return srsly.read_json(path)
    else:
        return {}


class Pipe:
    """This class is not instantiated directly. Components inherit from it, and
    it defines the interface that components should follow to function as
    components in a spaCy analysis pipeline.
    """

    name = None

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

    def begin_training(self, get_examples=lambda: [], pipeline=None, sgd=None):
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
        deserialize["cfg"] = lambda p: self.cfg.update(deserialize_config(p))
        deserialize["model"] = load_model
        util.from_disk(path, deserialize, exclude)
        return self
