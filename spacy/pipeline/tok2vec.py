from typing import Iterator, Sequence, Iterable, Optional, Dict
from thinc.api import Model, set_dropout_rate, Optimizer

from .pipe import Pipe
from ..gold import Example
from ..tokens import Doc
from ..vocab import Vocab
from ..language import Language
from ..util import link_vectors_to_models, minibatch, load_config_from_str


default_model_config = """
[model]
@architectures = "spacy.HashEmbedCNN.v1"
pretrained_vectors = null
width = 96
depth = 4
embed_size = 2000
window_size = 1
maxout_pieces = 3
subword_features = true
dropout = null
"""
DEFAULT_TOK2VEC_MODEL = load_config_from_str(
    default_model_config, create_objects=False
)["model"]


@Language.factory(
    "tok2vec", assigns=["doc.tensor"], default_config={"model": DEFAULT_TOK2VEC_MODEL}
)
def make_tok2vec(nlp: Language, name: str, model: Model):
    return Tok2Vec(nlp.vocab, model, name)


class Tok2Vec(Pipe):
    def __init__(self, vocab: Vocab, model: Model, name: str = "tok2vec"):
        """Construct a new statistical model. Weights are not allocated on
        initialisation.
        vocab (Vocab): A `Vocab` instance. The model must share the same `Vocab`
            instance with the `Doc` objects it will process.
        """
        self.vocab = vocab
        self.model = model
        self.name = name
        self.listeners = []
        self.cfg = {}

    def create_listener(self) -> None:
        listener = Tok2VecListener(
            upstream_name="tok2vec", width=self.model.get_dim("nO")
        )
        self.listeners.append(listener)

    def add_listener(self, listener: "Tok2VecListener") -> None:
        self.listeners.append(listener)

    def find_listeners(self, model: Model) -> None:
        for node in model.walk():
            if isinstance(node, Tok2VecListener) and node.upstream_name == self.name:
                self.add_listener(node)

    def __call__(self, doc: Doc) -> Doc:
        """Add context-sensitive vectors to a `Doc`, e.g. from a CNN or LSTM
        model. Vectors are set to the `Doc.tensor` attribute.
        docs (Doc or iterable): One or more documents to add vectors to.
        RETURNS (dict or None): Intermediate computations.
        """
        tokvecses = self.predict([doc])
        self.set_annotations([doc], tokvecses)
        return doc

    def pipe(self, stream: Iterator[Doc], batch_size: int = 128) -> Iterator[Doc]:
        """Process `Doc` objects as a stream.
        stream (iterator): A sequence of `Doc` objects to process.
        batch_size (int): Number of `Doc` objects to group.
        YIELDS (iterator): A sequence of `Doc` objects, in order of input.
        """
        for docs in minibatch(stream, batch_size):
            docs = list(docs)
            tokvecses = self.predict(docs)
            self.set_annotations(docs, tokvecses)
            yield from docs

    def predict(self, docs: Sequence[Doc]):
        """Return a single tensor for a batch of documents.
        docs (iterable): A sequence of `Doc` objects.
        RETURNS (object): Vector representations for each token in the documents.
        """
        tokvecs = self.model.predict(docs)
        batch_id = Tok2VecListener.get_batch_id(docs)
        for listener in self.listeners:
            listener.receive(batch_id, tokvecs, None)
        return tokvecs

    def set_annotations(self, docs: Sequence[Doc], tokvecses) -> None:
        """Set the tensor attribute for a batch of documents.
        docs (iterable): A sequence of `Doc` objects.
        tokvecs (object): Vector representation for each token in the documents.
        """
        for doc, tokvecs in zip(docs, tokvecses):
            assert tokvecs.shape[0] == len(doc)
            doc.tensor = tokvecs

    def update(
        self,
        examples: Iterable[Example],
        *,
        drop: float = 0.0,
        sgd: Optional[Optimizer] = None,
        losses: Optional[Dict[str, float]] = None,
        set_annotations: bool = False,
    ):
        """Update the model.
        examples (Iterable[Example]): A batch of examples
        drop (float): The droput rate.
        sgd (Optimizer): An optimizer.
        losses (Dict[str, float]): Dictionary to update with the loss, keyed by component.
        set_annotations (bool): whether or not to update the examples with the predictions
        RETURNS (Dict[str, float]): The updated losses dictionary
        """
        if losses is None:
            losses = {}
        docs = [eg.predicted for eg in examples]
        if isinstance(docs, Doc):
            docs = [docs]
        set_dropout_rate(self.model, drop)
        tokvecs, bp_tokvecs = self.model.begin_update(docs)

        d_tokvecs = [self.model.ops.alloc2f(*t2v.shape) for t2v in tokvecs]
        losses.setdefault(self.name, 0.0)

        def accumulate_gradient(one_d_tokvecs):
            """Accumulate tok2vec loss and gradient. This is passed as a callback
            to all but the last listener. Only the last one does the backprop.
            """
            nonlocal d_tokvecs
            for i in range(len(one_d_tokvecs)):
                d_tokvecs[i] += one_d_tokvecs[i]
                losses[self.name] += float((one_d_tokvecs[i] ** 2).sum())

        def backprop(one_d_tokvecs):
            """Callback to actually do the backprop. Passed to last listener."""
            accumulate_gradient(one_d_tokvecs)
            d_docs = bp_tokvecs(d_tokvecs)
            if sgd is not None:
                self.model.finish_update(sgd)
            return d_docs

        batch_id = Tok2VecListener.get_batch_id(docs)
        for listener in self.listeners[:-1]:
            listener.receive(batch_id, tokvecs, accumulate_gradient)
        self.listeners[-1].receive(batch_id, tokvecs, backprop)
        if set_annotations:
            self.set_annotations(docs, tokvecs)
        return losses

    def get_loss(self, docs, golds, scores):
        pass

    def begin_training(
        self, get_examples=lambda: [], pipeline=None, sgd=None, **kwargs
    ):
        """Allocate models and pre-process training data

        get_examples (function): Function returning example training data.
        pipeline (list): The pipeline the model is part of.
        """
        docs = [Doc(Vocab(), words=["hello"])]
        self.model.initialize(X=docs)
        link_vectors_to_models(self.vocab)


class Tok2VecListener(Model):
    """A layer that gets fed its answers from an upstream connection,
    for instance from a component earlier in the pipeline.
    """

    name = "tok2vec-listener"

    def __init__(self, upstream_name, width):
        Model.__init__(self, name=self.name, forward=forward, dims={"nO": width})
        self.upstream_name = upstream_name
        self._batch_id = None
        self._outputs = None
        self._backprop = None

    @classmethod
    def get_batch_id(cls, inputs):
        return sum(sum(token.orth for token in doc) for doc in inputs)

    def receive(self, batch_id, outputs, backprop):
        self._batch_id = batch_id
        self._outputs = outputs
        self._backprop = backprop

    def verify_inputs(self, inputs):
        if self._batch_id is None and self._outputs is None:
            raise ValueError("The Tok2Vec listener did not receive valid input.")
        else:
            batch_id = self.get_batch_id(inputs)
            if batch_id != self._batch_id:
                raise ValueError(f"Mismatched IDs! {batch_id} vs {self._batch_id}")
            else:
                return True


def forward(model: Tok2VecListener, inputs, is_train):
    if is_train:
        model.verify_inputs(inputs)
        return model._outputs, model._backprop
    else:
        return [doc.tensor for doc in inputs], lambda dX: []
