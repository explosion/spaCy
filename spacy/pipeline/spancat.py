from typing import List, Dict, Callable, Tuple, Optional, Iterable, Any
from thinc.api import Config, Model, get_current_ops, set_dropout_rate, Ops
from thinc.api import Optimizer
from thinc.types import Ragged, Ints2d, Floats2d

import numpy

from ..compat import Protocol, runtime_checkable
from ..scorer import Scorer
from ..language import Language
from .trainable_pipe import TrainablePipe
from ..tokens import Doc, SpanGroup, Span
from ..vocab import Vocab
from ..training import Example, validate_examples
from ..errors import Errors
from ..util import registry


spancat_default_config = """
[model]
@architectures = "spacy.SpanCategorizer.v1"
scorer = {"@layers": "spacy.LinearLogistic.v1"}

[model.reducer]
@layers = spacy.mean_max_reducer.v1
hidden_size = 128

[model.tok2vec]
@architectures = "spacy.Tok2Vec.v2"

[model.tok2vec.embed]
@architectures = "spacy.MultiHashEmbed.v2"
width = 96
rows = [5000, 2000, 1000, 1000]
attrs = ["ORTH", "PREFIX", "SUFFIX", "SHAPE"]
include_static_vectors = false

[model.tok2vec.encode]
@architectures = "spacy.MaxoutWindowEncoder.v2"
width = ${model.tok2vec.embed.width}
window_size = 1
maxout_pieces = 3
depth = 4
"""

DEFAULT_SPANCAT_MODEL = Config().from_str(spancat_default_config)["model"]


@runtime_checkable
class Suggester(Protocol):
    def __call__(self, docs: Iterable[Doc], *, ops: Optional[Ops] = None) -> Ragged:
        ...


@registry.misc("spacy.ngram_suggester.v1")
def build_ngram_suggester(sizes: List[int]) -> Suggester:
    """Suggest all spans of the given lengths. Spans are returned as a ragged
    array of integers. The array has two columns, indicating the start and end
    position."""

    def ngram_suggester(docs: Iterable[Doc], *, ops: Optional[Ops] = None) -> Ragged:
        if ops is None:
            ops = get_current_ops()
        spans = []
        lengths = []
        for doc in docs:
            starts = ops.xp.arange(len(doc), dtype="i")
            starts = starts.reshape((-1, 1))
            length = 0
            for size in sizes:
                if size <= len(doc):
                    starts_size = starts[: len(doc) - (size - 1)]
                    spans.append(ops.xp.hstack((starts_size, starts_size + size)))
                    length += spans[-1].shape[0]
                if spans:
                    assert spans[-1].ndim == 2, spans[-1].shape
            lengths.append(length)
        lengths_array = ops.asarray1i(lengths)
        if len(spans) > 0:
            output = Ragged(ops.xp.vstack(spans), lengths_array)
        else:
            output = Ragged(ops.xp.zeros((0, 0), dtype="i"), lengths_array)

        assert output.dataXd.ndim == 2
        return output

    return ngram_suggester


@registry.misc("spacy.ngram_range_suggester.v1")
def build_ngram_range_suggester(min_size: int, max_size: int) -> Suggester:
    """Suggest all spans of the given lengths between a given min and max value - both inclusive.
    Spans are returned as a ragged array of integers. The array has two columns,
    indicating the start and end position."""
    sizes = list(range(min_size, max_size + 1))
    return build_ngram_suggester(sizes)


@Language.factory(
    "spancat",
    assigns=["doc.spans"],
    default_config={
        "threshold": 0.5,
        "spans_key": "sc",
        "max_positive": None,
        "model": DEFAULT_SPANCAT_MODEL,
        "suggester": {"@misc": "spacy.ngram_suggester.v1", "sizes": [1, 2, 3]},
        "scorer": {"@scorers": "spacy.spancat_scorer.v1"},
    },
    default_score_weights={"spans_sc_f": 1.0, "spans_sc_p": 0.0, "spans_sc_r": 0.0},
)
def make_spancat(
    nlp: Language,
    name: str,
    suggester: Suggester,
    model: Model[Tuple[List[Doc], Ragged], Floats2d],
    spans_key: str,
    scorer: Optional[Callable],
    threshold: float,
    max_positive: Optional[int],
) -> "SpanCategorizer":
    """Create a SpanCategorizer component. The span categorizer consists of two
    parts: a suggester function that proposes candidate spans, and a labeller
    model that predicts one or more labels for each span.

    suggester (Callable[[Iterable[Doc], Optional[Ops]], Ragged]): A function that suggests spans.
        Spans are returned as a ragged array with two integer columns, for the
        start and end positions.
    model (Model[Tuple[List[Doc], Ragged], Floats2d]): A model instance that
        is given a list of documents and (start, end) indices representing
        candidate span offsets. The model predicts a probability for each category
        for each span.
    spans_key (str): Key of the doc.spans dict to save the spans under. During
        initialization and training, the component will look for spans on the
        reference document under the same key.
    scorer (Optional[Callable]): The scoring method. Defaults to
        Scorer.score_spans for the Doc.spans[spans_key] with overlapping
        spans allowed.
    threshold (float): Minimum probability to consider a prediction positive.
        Spans with a positive prediction will be saved on the Doc. Defaults to
        0.5.
    max_positive (Optional[int]): Maximum number of labels to consider positive
        per span. Defaults to None, indicating no limit.
    """
    return SpanCategorizer(
        nlp.vocab,
        suggester=suggester,
        model=model,
        spans_key=spans_key,
        threshold=threshold,
        max_positive=max_positive,
        name=name,
        scorer=scorer,
    )


def spancat_score(examples: Iterable[Example], **kwargs) -> Dict[str, Any]:
    kwargs = dict(kwargs)
    attr_prefix = "spans_"
    key = kwargs["spans_key"]
    kwargs.setdefault("attr", f"{attr_prefix}{key}")
    kwargs.setdefault("allow_overlap", True)
    kwargs.setdefault(
        "getter", lambda doc, key: doc.spans.get(key[len(attr_prefix) :], [])
    )
    kwargs.setdefault("has_annotation", lambda doc: key in doc.spans)
    return Scorer.score_spans(examples, **kwargs)


@registry.scorers("spacy.spancat_scorer.v1")
def make_spancat_scorer():
    return spancat_score


class SpanCategorizer(TrainablePipe):
    """Pipeline component to label spans of text.

    DOCS: https://spacy.io/api/spancategorizer
    """

    def __init__(
        self,
        vocab: Vocab,
        model: Model[Tuple[List[Doc], Ragged], Floats2d],
        suggester: Suggester,
        name: str = "spancat",
        *,
        spans_key: str = "spans",
        threshold: float = 0.5,
        max_positive: Optional[int] = None,
        scorer: Optional[Callable] = spancat_score,
    ) -> None:
        """Initialize the span categorizer.
        vocab (Vocab): The shared vocabulary.
        model (thinc.api.Model): The Thinc Model powering the pipeline component.
        name (str): The component instance name, used to add entries to the
            losses during training.
        spans_key (str): Key of the Doc.spans dict to save the spans under.
            During initialization and training, the component will look for
            spans on the reference document under the same key. Defaults to
            `"spans"`.
        threshold (float): Minimum probability to consider a prediction
            positive. Spans with a positive prediction will be saved on the Doc.
            Defaults to 0.5.
        max_positive (Optional[int]): Maximum number of labels to consider
            positive per span. Defaults to None, indicating no limit.
        scorer (Optional[Callable]): The scoring method. Defaults to
            Scorer.score_spans for the Doc.spans[spans_key] with overlapping
            spans allowed.

        DOCS: https://spacy.io/api/spancategorizer#init
        """
        self.cfg = {
            "labels": [],
            "spans_key": spans_key,
            "threshold": threshold,
            "max_positive": max_positive,
        }
        self.vocab = vocab
        self.suggester = suggester
        self.model = model
        self.name = name
        self.scorer = scorer

    @property
    def key(self) -> str:
        """Key of the doc.spans dict to save the spans under. During
        initialization and training, the component will look for spans on the
        reference document under the same key.
        """
        return str(self.cfg["spans_key"])

    def add_label(self, label: str) -> int:
        """Add a new label to the pipe.

        label (str): The label to add.
        RETURNS (int): 0 if label is already present, otherwise 1.

        DOCS: https://spacy.io/api/spancategorizer#add_label
        """
        if not isinstance(label, str):
            raise ValueError(Errors.E187)
        if label in self.labels:
            return 0
        self._allow_extra_label()
        self.cfg["labels"].append(label)  # type: ignore
        self.vocab.strings.add(label)
        return 1

    @property
    def labels(self) -> Tuple[str]:
        """RETURNS (Tuple[str]): The labels currently added to the component.

        DOCS: https://spacy.io/api/spancategorizer#labels
        """
        return tuple(self.cfg["labels"])  # type: ignore

    @property
    def label_data(self) -> List[str]:
        """RETURNS (List[str]): Information about the component's labels.

        DOCS: https://spacy.io/api/spancategorizer#label_data
        """
        return list(self.labels)

    def predict(self, docs: Iterable[Doc]):
        """Apply the pipeline's model to a batch of docs, without modifying them.

        docs (Iterable[Doc]): The documents to predict.
        RETURNS: The models prediction for each document.

        DOCS: https://spacy.io/api/spancategorizer#predict
        """
        indices = self.suggester(docs, ops=self.model.ops)
        if indices.lengths.sum() == 0:
            scores = self.model.ops.alloc2f(0, 0)
        else:
            scores = self.model.predict((docs, indices))  # type: ignore
        return indices, scores

    def set_candidates(
        self, docs: Iterable[Doc], *, candidates_key: str = "candidates"
    ) -> None:
        """Use the spancat suggester to add a list of span candidates to a list of docs.
        This method is intended to be used for debugging purposes.

        docs (Iterable[Doc]): The documents to modify.
        candidates_key (str): Key of the Doc.spans dict to save the candidate spans under.

        DOCS: https://spacy.io/api/spancategorizer#set_candidates
        """
        suggester_output = self.suggester(docs, ops=self.model.ops)

        for candidates, doc in zip(suggester_output, docs):  # type: ignore
            doc.spans[candidates_key] = []
            for index in candidates.dataXd:
                doc.spans[candidates_key].append(doc[index[0] : index[1]])

    def set_annotations(self, docs: Iterable[Doc], indices_scores) -> None:
        """Modify a batch of Doc objects, using pre-computed scores.

        docs (Iterable[Doc]): The documents to modify.
        scores: The scores to set, produced by SpanCategorizer.predict.

        DOCS: https://spacy.io/api/spancategorizer#set_annotations
        """
        labels = self.labels
        indices, scores = indices_scores
        offset = 0
        for i, doc in enumerate(docs):
            indices_i = indices[i].dataXd
            doc.spans[self.key] = self._make_span_group(
                doc, indices_i, scores[offset : offset + indices.lengths[i]], labels  # type: ignore[arg-type]
            )
            offset += indices.lengths[i]

    def update(
        self,
        examples: Iterable[Example],
        *,
        drop: float = 0.0,
        sgd: Optional[Optimizer] = None,
        losses: Optional[Dict[str, float]] = None,
    ) -> Dict[str, float]:
        """Learn from a batch of documents and gold-standard information,
        updating the pipe's model. Delegates to predict and get_loss.

        examples (Iterable[Example]): A batch of Example objects.
        drop (float): The dropout rate.
        sgd (thinc.api.Optimizer): The optimizer.
        losses (Dict[str, float]): Optional record of the loss during training.
            Updated using the component name as the key.
        RETURNS (Dict[str, float]): The updated losses dictionary.

        DOCS: https://spacy.io/api/spancategorizer#update
        """
        if losses is None:
            losses = {}
        losses.setdefault(self.name, 0.0)
        validate_examples(examples, "SpanCategorizer.update")
        self._validate_categories(examples)
        if not any(len(eg.predicted) if eg.predicted else 0 for eg in examples):
            # Handle cases where there are no tokens in any docs.
            return losses
        docs = [eg.predicted for eg in examples]
        spans = self.suggester(docs, ops=self.model.ops)
        if spans.lengths.sum() == 0:
            return losses
        set_dropout_rate(self.model, drop)
        scores, backprop_scores = self.model.begin_update((docs, spans))
        loss, d_scores = self.get_loss(examples, (spans, scores))
        backprop_scores(d_scores)  # type: ignore
        if sgd is not None:
            self.finish_update(sgd)
        losses[self.name] += loss
        return losses

    def get_loss(
        self, examples: Iterable[Example], spans_scores: Tuple[Ragged, Floats2d]
    ) -> Tuple[float, float]:
        """Find the loss and gradient of loss for the batch of documents and
        their predicted scores.

        examples (Iterable[Examples]): The batch of examples.
        spans_scores: Scores representing the model's predictions.
        RETURNS (Tuple[float, float]): The loss and the gradient.

        DOCS: https://spacy.io/api/spancategorizer#get_loss
        """
        spans, scores = spans_scores
        spans = Ragged(
            self.model.ops.to_numpy(spans.data), self.model.ops.to_numpy(spans.lengths)
        )
        label_map = {label: i for i, label in enumerate(self.labels)}
        target = numpy.zeros(scores.shape, dtype=scores.dtype)
        offset = 0
        for i, eg in enumerate(examples):
            # Map (start, end) offset of spans to the row in the d_scores array,
            # so that we can adjust the gradient for predictions that were
            # in the gold standard.
            spans_index = {}
            spans_i = spans[i].dataXd
            for j in range(spans.lengths[i]):
                start = int(spans_i[j, 0])  # type: ignore
                end = int(spans_i[j, 1])  # type: ignore
                spans_index[(start, end)] = offset + j
            for gold_span in self._get_aligned_spans(eg):
                key = (gold_span.start, gold_span.end)
                if key in spans_index:
                    row = spans_index[key]
                    k = label_map[gold_span.label_]
                    target[row, k] = 1.0
            # The target is a flat array for all docs. Track the position
            # we're at within the flat array.
            offset += spans.lengths[i]
        target = self.model.ops.asarray(target, dtype="f")  # type: ignore
        # The target will have the values 0 (for untrue predictions) or 1
        # (for true predictions).
        # The scores should be in the range [0, 1].
        # If the prediction is 0.9 and it's true, the gradient
        # will be -0.1 (0.9 - 1.0).
        # If the prediction is 0.9 and it's false, the gradient will be
        # 0.9 (0.9 - 0.0)
        d_scores = scores - target
        loss = float((d_scores**2).sum())
        return loss, d_scores

    def initialize(
        self,
        get_examples: Callable[[], Iterable[Example]],
        *,
        nlp: Optional[Language] = None,
        labels: Optional[List[str]] = None,
    ) -> None:
        """Initialize the pipe for training, using a representative set
        of data examples.

        get_examples (Callable[[], Iterable[Example]]): Function that
            returns a representative sample of gold-standard Example objects.
        nlp (Optional[Language]): The current nlp object the component is part of.
        labels (Optional[List[str]]): The labels to add to the component, typically generated by the
            `init labels` command. If no labels are provided, the get_examples
            callback is used to extract the labels from the data.

        DOCS: https://spacy.io/api/spancategorizer#initialize
        """
        subbatch: List[Example] = []
        if labels is not None:
            for label in labels:
                self.add_label(label)
        for eg in get_examples():
            if labels is None:
                for span in eg.reference.spans.get(self.key, []):
                    self.add_label(span.label_)
            if len(subbatch) < 10:
                subbatch.append(eg)
        self._require_labels()
        if subbatch:
            docs = [eg.x for eg in subbatch]
            spans = build_ngram_suggester(sizes=[1])(docs)
            Y = self.model.ops.alloc2f(spans.dataXd.shape[0], len(self.labels))
            self.model.initialize(X=(docs, spans), Y=Y)
        else:
            self.model.initialize()

    def _validate_categories(self, examples: Iterable[Example]):
        # TODO
        pass

    def _get_aligned_spans(self, eg: Example):
        return eg.get_aligned_spans_y2x(
            eg.reference.spans.get(self.key, []), allow_overlap=True
        )

    def _make_span_group(
        self, doc: Doc, indices: Ints2d, scores: Floats2d, labels: List[str]
    ) -> SpanGroup:
        spans = SpanGroup(doc, name=self.key)
        max_positive = self.cfg["max_positive"]
        threshold = self.cfg["threshold"]

        keeps = scores >= threshold
        ranked = (scores * -1).argsort()  # type: ignore
        if max_positive is not None:
            assert isinstance(max_positive, int)
            span_filter = ranked[:, max_positive:]
            for i, row in enumerate(span_filter):
                keeps[i, row] = False
        spans.attrs["scores"] = scores[keeps].flatten()

        indices = self.model.ops.to_numpy(indices)
        keeps = self.model.ops.to_numpy(keeps)

        for i in range(indices.shape[0]):
            start = indices[i, 0]
            end = indices[i, 1]

            for j, keep in enumerate(keeps[i]):
                if keep:
                    spans.append(Span(doc, start, end, label=labels[j]))

        return spans
