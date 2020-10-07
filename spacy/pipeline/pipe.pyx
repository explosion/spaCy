# cython: infer_types=True, profile=True
import warnings
from typing import Optional, Tuple
import srsly
from thinc.api import set_dropout_rate, Model

from ..tokens.doc cimport Doc

from ..training import validate_examples
from ..errors import Errors, Warnings
from .. import util


cdef class Pipe:
    """This class is a base class and not instantiated directly. Trainable
    pipeline components like the EntityRecognizer or TextCategorizer inherit
    from it and it defines the interface that components should follow to
    function as trainable components in a spaCy pipeline.

    DOCS: https://nightly.spacy.io/api/pipe
    """
    def __init__(self, vocab, model, name, **cfg):
        """Initialize a pipeline component.

        vocab (Vocab): The shared vocabulary.
        model (thinc.api.Model): The Thinc Model powering the pipeline component.
        name (str): The component instance name.
        **cfg: Additonal settings and config parameters.

        DOCS: https://nightly.spacy.io/api/pipe#init
        """
        self.vocab = vocab
        self.model = model
        self.name = name
        self.cfg = dict(cfg)

    @classmethod
    def __init_subclass__(cls, **kwargs):
        """Raise a warning if an inheriting class implements 'begin_training'
         (from v2) instead of the new 'initialize' method (from v3)"""
        if hasattr(cls, "begin_training"):
            warnings.warn(Warnings.W088.format(name=cls.__name__))

    @property
    def labels(self) -> Optional[Tuple[str]]:
        return []

    @property
    def label_data(self):
        """Optional JSON-serializable data that would be sufficient to recreate
        the label set if provided to the `pipe.initialize()` method.
        """
        return None

    def __call__(self, Doc doc):
        """Apply the pipe to one document. The document is modified in place,
        and returned. This usually happens under the hood when the nlp object
        is called on a text and all components are applied to the Doc.

        docs (Doc): The Doc to process.
        RETURNS (Doc): The processed Doc.

        DOCS: https://nightly.spacy.io/api/pipe#call
        """
        scores = self.predict([doc])
        self.set_annotations([doc], scores)
        return doc

    def pipe(self, stream, *, batch_size=128):
        """Apply the pipe to a stream of documents. This usually happens under
        the hood when the nlp object is called on a text and all components are
        applied to the Doc.

        stream (Iterable[Doc]): A stream of documents.
        batch_size (int): The number of documents to buffer.
        YIELDS (Doc): Processed documents in order.

        DOCS: https://nightly.spacy.io/api/pipe#pipe
        """
        for docs in util.minibatch(stream, size=batch_size):
            scores = self.predict(docs)
            self.set_annotations(docs, scores)
            yield from docs

    def predict(self, docs):
        """Apply the pipeline's model to a batch of docs, without modifying them.
        Returns a single tensor for a batch of documents.

        docs (Iterable[Doc]): The documents to predict.
        RETURNS: Vector representations for each token in the documents.

        DOCS: https://nightly.spacy.io/api/pipe#predict
        """
        raise NotImplementedError(Errors.E931.format(method="predict", name=self.name))

    def set_annotations(self, docs, scores):
        """Modify a batch of documents, using pre-computed scores.

        docs (Iterable[Doc]): The documents to modify.
        scores: The scores to assign.

        DOCS: https://nightly.spacy.io/api/pipe#set_annotations
        """
        raise NotImplementedError(Errors.E931.format(method="set_annotations", name=self.name))

    def update(self, examples, *, drop=0.0, set_annotations=False, sgd=None, losses=None):
        """Learn from a batch of documents and gold-standard information,
        updating the pipe's model. Delegates to predict and get_loss.

        examples (Iterable[Example]): A batch of Example objects.
        drop (float): The dropout rate.
        set_annotations (bool): Whether or not to update the Example objects
            with the predictions.
        sgd (thinc.api.Optimizer): The optimizer.
        losses (Dict[str, float]): Optional record of the loss during training.
            Updated using the component name as the key.
        RETURNS (Dict[str, float]): The updated losses dictionary.

        DOCS: https://nightly.spacy.io/api/pipe#update
        """
        if losses is None:
            losses = {}
        if not hasattr(self, "model") or self.model in (None, True, False):
            return losses
        losses.setdefault(self.name, 0.0)
        validate_examples(examples, "Pipe.update")
        if not any(len(eg.predicted) if eg.predicted else 0 for eg in examples):
            # Handle cases where there are no tokens in any docs.
            return
        set_dropout_rate(self.model, drop)
        scores, bp_scores = self.model.begin_update([eg.predicted for eg in examples])
        loss, d_scores = self.get_loss(examples, scores)
        bp_scores(d_scores)
        if sgd not in (None, False):
            self.finish_update(sgd)
        losses[self.name] += loss
        if set_annotations:
            docs = [eg.predicted for eg in examples]
            self.set_annotations(docs, scores=scores)
        return losses

    def rehearse(self, examples, *, sgd=None, losses=None, **config):
        """Perform a "rehearsal" update from a batch of data. Rehearsal updates
        teach the current model to make predictions similar to an initial model,
        to try to address the "catastrophic forgetting" problem. This feature is
        experimental.

        examples (Iterable[Example]): A batch of Example objects.
        drop (float): The dropout rate.
        sgd (thinc.api.Optimizer): The optimizer.
        losses (Dict[str, float]): Optional record of the loss during training.
            Updated using the component name as the key.
        RETURNS (Dict[str, float]): The updated losses dictionary.

        DOCS: https://nightly.spacy.io/api/pipe#rehearse
        """
        pass

    def get_loss(self, examples, scores):
        """Find the loss and gradient of loss for the batch of documents and
        their predicted scores.

        examples (Iterable[Examples]): The batch of examples.
        scores: Scores representing the model's predictions.
        RETURNS (Tuple[float, float]): The loss and the gradient.

        DOCS: https://nightly.spacy.io/api/pipe#get_loss
        """
        raise NotImplementedError(Errors.E931.format(method="get_loss", name=self.name))

    def add_label(self, label):
        """Add an output label, to be predicted by the model. It's possible to
        extend pretrained models with new labels, but care should be taken to
        avoid the "catastrophic forgetting" problem.

        label (str): The label to add.
        RETURNS (int): 0 if label is already present, otherwise 1.

        DOCS: https://nightly.spacy.io/api/pipe#add_label
        """
        raise NotImplementedError(Errors.E931.format(method="add_label", name=self.name))


    def _require_labels(self) -> None:
        """Raise an error if the component's model has no labels defined."""
        if not self.labels or list(self.labels) == [""]:
            raise ValueError(Errors.E143.format(name=self.name))


    def _allow_extra_label(self) -> None:
        """Raise an error if the component can not add any more labels."""
        if self.model.has_dim("nO") and self.model.get_dim("nO") == len(self.labels):
            if not self.is_resizable():
                raise ValueError(Errors.E922.format(name=self.name, nO=self.model.get_dim("nO")))


    def create_optimizer(self):
        """Create an optimizer for the pipeline component.

        RETURNS (thinc.api.Optimizer): The optimizer.

        DOCS: https://nightly.spacy.io/api/pipe#create_optimizer
        """
        return util.create_default_optimizer()

    def initialize(self, get_examples, *, nlp=None):
        """Initialize the pipe for training, using data examples if available.
        This method needs to be implemented by each Pipe component,
        ensuring the internal model (if available) is initialized properly
        using the provided sample of Example objects.

        get_examples (Callable[[], Iterable[Example]]): Function that
            returns a representative sample of gold-standard Example objects.
        nlp (Language): The current nlp object the component is part of.

        DOCS: https://nightly.spacy.io/api/pipe#initialize
        """
        pass

    def _ensure_examples(self, get_examples):
        if get_examples is None or not hasattr(get_examples, "__call__"):
            err = Errors.E930.format(name=self.name, obj=type(get_examples))
            raise ValueError(err)
        if not get_examples():
            err = Errors.E930.format(name=self.name, obj=get_examples())
            raise ValueError(err)

    def is_resizable(self):
        return hasattr(self, "model") and "resize_output" in self.model.attrs

    def is_trainable(self):
        return hasattr(self, "model") and isinstance(self.model, Model)

    def set_output(self, nO):
        if self.is_resizable():
            self.model.attrs["resize_output"](self.model, nO)
        else:
            raise NotImplementedError(Errors.E921)

    def use_params(self, params):
        """Modify the pipe's model, to use the given parameter values. At the
        end of the context, the original parameters are restored.

        params (dict): The parameter values to use in the model.

        DOCS: https://nightly.spacy.io/api/pipe#use_params
        """
        with self.model.use_params(params):
            yield

    def finish_update(self, sgd):
        """Update parameters using the current parameter gradients.
        The Optimizer instance contains the functionality to perform
        the stochastic gradient descent.

        sgd (thinc.api.Optimizer): The optimizer.

        DOCS: https://nightly.spacy.io/api/pipe#finish_update
        """
        self.model.finish_update(sgd)

    def score(self, examples, **kwargs):
        """Score a batch of examples.

        examples (Iterable[Example]): The examples to score.
        RETURNS (Dict[str, Any]): The scores.

        DOCS: https://nightly.spacy.io/api/pipe#score
        """
        return {}

    def to_bytes(self, *, exclude=tuple()):
        """Serialize the pipe to a bytestring.

        exclude (Iterable[str]): String names of serialization fields to exclude.
        RETURNS (bytes): The serialized object.

        DOCS: https://nightly.spacy.io/api/pipe#to_bytes
        """
        serialize = {}
        serialize["cfg"] = lambda: srsly.json_dumps(self.cfg)
        serialize["model"] = self.model.to_bytes
        if hasattr(self, "vocab"):
            serialize["vocab"] = self.vocab.to_bytes
        return util.to_bytes(serialize, exclude)

    def from_bytes(self, bytes_data, *, exclude=tuple()):
        """Load the pipe from a bytestring.

        exclude (Iterable[str]): String names of serialization fields to exclude.
        RETURNS (Pipe): The loaded object.

        DOCS: https://nightly.spacy.io/api/pipe#from_bytes
        """

        def load_model(b):
            try:
                self.model.from_bytes(b)
            except AttributeError:
                raise ValueError(Errors.E149) from None

        deserialize = {}
        if hasattr(self, "vocab"):
            deserialize["vocab"] = lambda b: self.vocab.from_bytes(b)
        deserialize["cfg"] = lambda b: self.cfg.update(srsly.json_loads(b))
        deserialize["model"] = load_model
        util.from_bytes(bytes_data, deserialize, exclude)
        return self

    def to_disk(self, path, *, exclude=tuple()):
        """Serialize the pipe to disk.

        path (str / Path): Path to a directory.
        exclude (Iterable[str]): String names of serialization fields to exclude.

        DOCS: https://nightly.spacy.io/api/pipe#to_disk
        """
        serialize = {}
        serialize["cfg"] = lambda p: srsly.write_json(p, self.cfg)
        serialize["vocab"] = lambda p: self.vocab.to_disk(p)
        serialize["model"] = lambda p: self.model.to_disk(p)
        util.to_disk(path, serialize, exclude)

    def from_disk(self, path, *, exclude=tuple()):
        """Load the pipe from disk.

        path (str / Path): Path to a directory.
        exclude (Iterable[str]): String names of serialization fields to exclude.
        RETURNS (Pipe): The loaded object.

        DOCS: https://nightly.spacy.io/api/pipe#from_disk
        """

        def load_model(p):
            try:
                self.model.from_bytes(p.open("rb").read())
            except AttributeError:
                raise ValueError(Errors.E149) from None

        deserialize = {}
        deserialize["vocab"] = lambda p: self.vocab.from_disk(p)
        deserialize["cfg"] = lambda p: self.cfg.update(deserialize_config(p))
        deserialize["model"] = load_model
        util.from_disk(path, deserialize, exclude)
        return self


def deserialize_config(path):
    if path.exists():
        return srsly.read_json(path)
    else:
        return {}
