from typing import Iterator, Sequence, Iterable, Optional, Dict, Callable, List
from thinc.api import Model, set_dropout_rate, Optimizer, Config
from itertools import islice

from .trainable_pipe import TrainablePipe
from ..training import Example, validate_examples, validate_get_examples
from ..tokens import Doc
from ..vocab import Vocab
from ..language import Language
from ..errors import Errors
from ..util import minibatch


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
"""
DEFAULT_TOK2VEC_MODEL = Config().from_str(default_model_config)["model"]


@Language.factory(
    "tok2vec", assigns=["doc.tensor"], default_config={"model": DEFAULT_TOK2VEC_MODEL}
)
def make_tok2vec(nlp: Language, name: str, model: Model) -> "Tok2Vec":
    return Tok2Vec(nlp.vocab, model, name)


class Tok2Vec(TrainablePipe):
    """Apply a "token-to-vector" model and set its outputs in the doc.tensor
    attribute. This is mostly useful to share a single subnetwork between multiple
    components, e.g. to have one embedding and CNN network shared between a
    parser, tagger and NER.

    In order to use the `Tok2Vec` predictions, subsequent components should use
    the `Tok2VecListener` layer as the tok2vec subnetwork of their model. This
    layer will read data from the `doc.tensor` attribute during prediction.
    During training, the `Tok2Vec` component will save its prediction and backprop
    callback for each batch, so that the subsequent components can backpropagate
    to the shared weights. This implementation is used because it allows us to
    avoid relying on object identity within the models to achieve the parameter
    sharing.
    """

    def __init__(self, vocab: Vocab, model: Model, name: str = "tok2vec") -> None:
        """Initialize a tok2vec component.

        vocab (Vocab): The shared vocabulary.
        model (thinc.api.Model[List[Doc], List[Floats2d]]):
            The Thinc Model powering the pipeline component. It should take
            a list of Doc objects as input, and output a list of 2d float arrays.
        name (str): The component instance name.

        DOCS: https://nightly.spacy.io/api/tok2vec#init
        """
        self.vocab = vocab
        self.model = model
        self.name = name
        self.listeners = []
        self.cfg = {}

    def add_listener(self, listener: "Tok2VecListener") -> None:
        """Add a listener for a downstream component. Usually internals."""
        self.listeners.append(listener)

    def find_listeners(self, model: Model) -> None:
        """Walk over a model, looking for layers that are Tok2vecListener
        subclasses that have an upstream_name that matches this component.
        Listeners can also set their upstream_name attribute to the wildcard
        string '*' to match any `Tok2Vec`.

        You're unlikely to ever need multiple `Tok2Vec` components, so it's
        fine to leave your listeners upstream_name on '*'.
        """
        for node in model.walk():
            if isinstance(node, Tok2VecListener) and node.upstream_name in (
                "*",
                self.name,
            ):
                self.add_listener(node)

    def __call__(self, doc: Doc) -> Doc:
        """Add context-sensitive embeddings to the Doc.tensor attribute, allowing
        them to be used as features by downstream components.

        docs (Doc): The Doc to process.
        RETURNS (Doc): The processed Doc.

        DOCS: https://nightly.spacy.io/api/tok2vec#call
        """
        tokvecses = self.predict([doc])
        self.set_annotations([doc], tokvecses)
        return doc

    def pipe(self, stream: Iterator[Doc], *, batch_size: int = 128) -> Iterator[Doc]:
        """Apply the pipe to a stream of documents. This usually happens under
        the hood when the nlp object is called on a text and all components are
        applied to the Doc.

        stream (Iterable[Doc]): A stream of documents.
        batch_size (int): The number of documents to buffer.
        YIELDS (Doc): Processed documents in order.

        DOCS: https://nightly.spacy.io/api/tok2vec#pipe
        """
        for docs in minibatch(stream, batch_size):
            docs = list(docs)
            tokvecses = self.predict(docs)
            self.set_annotations(docs, tokvecses)
            yield from docs

    def predict(self, docs: Iterable[Doc]):
        """Apply the pipeline's model to a batch of docs, without modifying them.
        Returns a single tensor for a batch of documents.

        docs (Iterable[Doc]): The documents to predict.
        RETURNS: Vector representations for each token in the documents.

        DOCS: https://nightly.spacy.io/api/tok2vec#predict
        """
        tokvecs = self.model.predict(docs)
        batch_id = Tok2VecListener.get_batch_id(docs)
        for listener in self.listeners:
            listener.receive(batch_id, tokvecs, lambda dX: [])
        return tokvecs

    def set_annotations(self, docs: Sequence[Doc], tokvecses) -> None:
        """Modify a batch of documents, using pre-computed scores.

        docs (Iterable[Doc]): The documents to modify.
        tokvecses: The tensors to set, produced by Tok2Vec.predict.

        DOCS: https://nightly.spacy.io/api/tok2vec#set_annotations
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
        """Learn from a batch of documents and gold-standard information,
        updating the pipe's model.

        examples (Iterable[Example]): A batch of Example objects.
        drop (float): The dropout rate.
        set_annotations (bool): Whether or not to update the Example objects
            with the predictions.
        sgd (thinc.api.Optimizer): The optimizer.
        losses (Dict[str, float]): Optional record of the loss during training.
            Updated using the component name as the key.
        RETURNS (Dict[str, float]): The updated losses dictionary.

        DOCS: https://nightly.spacy.io/api/tok2vec#update
        """
        if losses is None:
            losses = {}
        validate_examples(examples, "Tok2Vec.update")
        docs = [eg.predicted for eg in examples]
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
                self.finish_update(sgd)
            return d_docs

        batch_id = Tok2VecListener.get_batch_id(docs)
        for listener in self.listeners[:-1]:
            listener.receive(batch_id, tokvecs, accumulate_gradient)
        if self.listeners:
            self.listeners[-1].receive(batch_id, tokvecs, backprop)
        if set_annotations:
            self.set_annotations(docs, tokvecs)
        return losses

    def get_loss(self, examples, scores) -> None:
        pass

    def initialize(
        self,
        get_examples: Callable[[], Iterable[Example]],
        *,
        nlp: Optional[Language] = None,
    ):
        """Initialize the pipe for training, using a representative set
        of data examples.

        get_examples (Callable[[], Iterable[Example]]): Function that
            returns a representative sample of gold-standard Example objects.
        nlp (Language): The current nlp object the component is part of.

        DOCS: https://nightly.spacy.io/api/tok2vec#initialize
        """
        validate_get_examples(get_examples, "Tok2Vec.initialize")
        doc_sample = []
        for example in islice(get_examples(), 10):
            doc_sample.append(example.x)
        assert doc_sample, Errors.E923.format(name=self.name)
        self.model.initialize(X=doc_sample)

    def add_label(self, label):
        raise NotImplementedError


class Tok2VecListener(Model):
    """A layer that gets fed its answers from an upstream connection,
    for instance from a component earlier in the pipeline.

    The Tok2VecListener layer is used as a sublayer within a component such
    as a parser, NER or text categorizer. Usually you'll have multiple listeners
    connecting to a single upstream Tok2Vec component, that's earlier in the
    pipeline. The Tok2VecListener layers act as proxies, passing the predictions
    from the Tok2Vec component into downstream components, and communicating
    gradients back upstream.
    """

    name = "tok2vec-listener"

    def __init__(self, upstream_name: str, width: int) -> None:
        """
        upstream_name (str): A string to identify the 'upstream' Tok2Vec component
            to communicate with. The upstream name should either be the wildcard
            string '*', or the name of the `Tok2Vec` component. You'll almost
            never have multiple upstream Tok2Vec components, so the wildcard
            string will almost always be fine.
        width (int):
            The width of the vectors produced by the upstream tok2vec component.
        """
        Model.__init__(self, name=self.name, forward=forward, dims={"nO": width})
        self.upstream_name = upstream_name
        self._batch_id = None
        self._outputs = None
        self._backprop = None

    @classmethod
    def get_batch_id(cls, inputs: List[Doc]) -> int:
        """Calculate a content-sensitive hash of the batch of documents, to check
        whether the next batch of documents is unexpected.
        """
        return sum(sum(token.orth for token in doc) for doc in inputs)

    def receive(self, batch_id: int, outputs, backprop) -> None:
        """Store a batch of training predictions and a backprop callback. The
        predictions and callback are produced by the upstream Tok2Vec component,
        and later will be used when the listener's component's model is called.
        """
        self._batch_id = batch_id
        self._outputs = outputs
        self._backprop = backprop

    def verify_inputs(self, inputs) -> bool:
        """Check that the batch of Doc objects matches the ones we have a
        prediction for.
        """
        if self._batch_id is None and self._outputs is None:
            raise ValueError(Errors.E954)
        else:
            batch_id = self.get_batch_id(inputs)
            if batch_id != self._batch_id:
                raise ValueError(Errors.E953.format(id1=batch_id, id2=self._batch_id))
            else:
                return True


def forward(model: Tok2VecListener, inputs, is_train: bool):
    """Supply the outputs from the upstream Tok2Vec component."""
    if is_train:
        model.verify_inputs(inputs)
        return model._outputs, model._backprop
    else:
        # This is pretty grim, but it's hard to do better :(.
        # It's hard to avoid relying on the doc.tensor attribute, because the
        # pipeline components can batch the data differently during prediction.
        # That doesn't happen in update, where the nlp object works on batches
        # of data.
        # When the components batch differently, we don't receive a matching
        # prediction from the upstream, so we can't predict.
        if not all(doc.tensor.size for doc in inputs):
            # But we do need to do *something* if the tensor hasn't been set.
            # The compromise is to at least return data of the right shape,
            # so the output is valid.
            width = model.get_dim("nO")
            outputs = [model.ops.alloc2f(len(doc), width) for doc in inputs]
        else:
            outputs = [doc.tensor for doc in inputs]
        return outputs, lambda dX: []
