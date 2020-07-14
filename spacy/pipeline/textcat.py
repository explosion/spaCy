import numpy
from typing import Iterable

from thinc.api import get_array_module, Model
from thinc.api import set_dropout_rate

from .pipes import Pipe
from ..language import Language
from ..util import link_vectors_to_models, load_config_from_str
from ..errors import Errors
from .. import util
from ..tokens import Doc
from ..vocab import Vocab


default_model_config = """
[model]
@architectures = "spacy.TextCat.v1"
exclusive_classes = false
pretrained_vectors = null
width = 64
conv_depth = 2
embed_size = 2000
window_size = 1
ngram_size = 1
dropout = null
"""
DEFAULT_TEXTCAT_MODEL = load_config_from_str(default_model_config, create_objects=False)["model"]

bow_model_config = """
[model]
@architectures = "spacy.TextCatBOW.v1"
exclusive_classes = false
ngram_size: 1
no_output_layer: false
"""

cnn_model_config = """
[model]
@architectures = "spacy.TextCatCNN.v1"
exclusive_classes = false

[model.tok2vec]
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


@Language.factory(
    "textcat",
    assigns=["doc.cats"],
    default_config={"labels": tuple(), "model": DEFAULT_TEXTCAT_MODEL},
)
def make_textcat(nlp: Language, name: str, model: Model, labels: Iterable[str]):
    return TextCategorizer(nlp.vocab, model, name, labels=labels)


class TextCategorizer(Pipe):
    """Pipeline component for text classification.

    DOCS: https://spacy.io/api/textcategorizer
    """

    def __init__(self, vocab, model, name="textcat", labels=tuple()):
        self.vocab = vocab
        self.model = model
        self.name = name
        self._rehearsal_model = None
        cfg = {"labels": labels}
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

    def update(
        self, examples, *, drop=0.0, set_annotations=False, sgd=None, losses=None
    ):
        if losses is None:
            losses = {}
        losses.setdefault(self.name, 0.0)
        try:
            if not any(len(eg.predicted) if eg.predicted else 0 for eg in examples):
                # Handle cases where there are no tokens in any docs.
                return losses
        except AttributeError:
            types = set([type(eg) for eg in examples])
            raise TypeError(
                Errors.E978.format(name="TextCategorizer", method="update", types=types)
            )
        set_dropout_rate(self.model, drop)
        scores, bp_scores = self.model.begin_update([eg.predicted for eg in examples])
        loss, d_scores = self.get_loss(examples, scores)
        bp_scores(d_scores)
        if sgd is not None:
            self.model.finish_update(sgd)
        losses[self.name] += loss
        if set_annotations:
            docs = [eg.predicted for eg in examples]
            self.set_annotations(docs, scores=scores)
        return losses

    def rehearse(self, examples, drop=0.0, sgd=None, losses=None):
        if self._rehearsal_model is None:
            return
        try:
            docs = [eg.predicted for eg in examples]
        except AttributeError:
            types = set([type(eg) for eg in examples])
            raise TypeError(
                Errors.E978.format(
                    name="TextCategorizer", method="rehearse", types=types
                )
            )
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
            losses[self.name] += (gradient ** 2).sum()

    def _examples_to_truth(self, examples):
        truths = numpy.zeros((len(examples), len(self.labels)), dtype="f")
        not_missing = numpy.ones((len(examples), len(self.labels)), dtype="f")
        for i, eg in enumerate(examples):
            for j, label in enumerate(self.labels):
                if label in eg.reference.cats:
                    truths[i, j] = eg.reference.cats[label]
                else:
                    not_missing[i, j] = 0.0
        truths = self.model.ops.asarray(truths)
        return truths, not_missing

    def get_loss(self, examples, scores):
        truths, not_missing = self._examples_to_truth(examples)
        not_missing = self.model.ops.asarray(not_missing)
        d_scores = (scores - truths) / scores.shape[0]
        d_scores *= not_missing
        mean_square_error = (d_scores ** 2).sum(axis=1).mean()
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

    def begin_training(
        self, get_examples=lambda: [], pipeline=None, sgd=None, **kwargs
    ):
        # TODO: begin_training is not guaranteed to see all data / labels ?
        examples = list(get_examples())
        for example in examples:
            try:
                y = example.y
            except AttributeError:
                raise TypeError(
                    Errors.E978.format(
                        name="TextCategorizer", method="update", types=type(example)
                    )
                )
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
