from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, cast

import numpy
from thinc.api import Config, Model, Ops, Optimizer
from thinc.api import set_dropout_rate
from thinc.types import Floats2d, Ints2d, Ragged

from ..compat import Protocol, runtime_checkable
from ..errors import Errors
from ..language import Language
from ..tokens import Doc, Span, SpanGroup
from ..training import Example, validate_examples
from ..vocab import Vocab
from .spancat import spancat_score, build_ngram_suggester
from .trainable_pipe import TrainablePipe


spancat_exclusive_default_config = """
[model]
@architectures = "spacy.SpanCategorizer.v1"
scorer = {"@layers": "Softmax.v2"}

[model.reducer]
@layers = spacy.mean_max_reducer.v1
hidden_size = 128

[model.tok2vec]
@architectures = "spacy.Tok2Vec.v2"
[model.tok2vec.embed]
@architectures = "spacy.MultiHashEmbed.v1"
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

DEFAULT_SPANCAT_MODEL = Config().from_str(spancat_exclusive_default_config)["model"]


@runtime_checkable
class Suggester(Protocol):
    def __call__(self, docs: Iterable[Doc], *, ops: Optional[Ops] = None) -> Ragged:
        ...


@Language.factory(
    "spancat_exclusive",
    assigns=["doc.spans"],
    default_config={
        "spans_key": "sc",
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
    negative_weight: float = 1.0,
    allow_overlap: bool = True,
) -> "SpanCategorizerExclusive":
    """Create a SpanCategorizerExclusive component. The span categorizer consists of two
    parts: a suggester function that proposes candidate spans, and a labeller
    model that predicts a single label for each span.

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
    negative_weight (float): Multiplier for the loss terms.
        Can be used to down weigh the negative samples if there are too many.
    allow_overlap (bool): If True the data is assumed to
        contain overlapping spans.
    """
    return SpanCategorizerExclusive(
        nlp.vocab,
        suggester=suggester,
        model=model,
        spans_key=spans_key,
        negative_weight=negative_weight,
        name=name,
        scorer=scorer,
        allow_overlap=allow_overlap,
    )


@dataclass
class Ranges:
    """
    Helper class help avoid storing overlapping span.
    """

    def __init__(self):
        self.ranges = set()

    def add(self, i, j):
        for e in range(i, j):
            self.ranges.add(e)

    def __contains__(self, rang):
        i, j = rang
        for e in range(i, j):
            if e in self.ranges:
                return True
        return False


class SpanCategorizerExclusive(TrainablePipe):
    """Pipeline component to label spans of text.

    DOCS: https://spacy.io/api/spancategorizerexclusive
    """

    def __init__(
        self,
        vocab: Vocab,
        model: Model[Tuple[List[Doc], Ragged], Floats2d],
        suggester: Suggester,
        name: str = "spancat_exclusive",
        *,
        spans_key: str = "spans",
        negative_weight: float = 1.0,
        allow_overlap: bool = True,
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
        negative_weight (float): Multiplier for the loss terms.
            Can be used to down weigh the negative samples if there are too many.
        allow_overlap (bool): If True the data is assumed to
            contain overlapping spans.
        scorer (Optional[Callable]): The scoring method. Defaults to
            Scorer.score_spans for the Doc.spans[spans_key] with overlapping
            spans allowed.

        DOCS: https://spacy.io/api/spancategorizerexclusive#init
        """
        self.cfg = {
            "labels": [],
            "spans_key": spans_key,
            "negative_weight": negative_weight,
            "allow_overlap": allow_overlap,
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

        DOCS: https://spacy.io/api/spancategorizerexclusive#add_label
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

        DOCS: https://spacy.io/api/spancategorizerexclusive#labels
        """
        return tuple(self.cfg["labels"])  # type: ignore

    @property
    def label_data(self) -> List[str]:
        """RETURNS (List[str]): Information about the component's labels.

        DOCS: https://spacy.io/api/spancategorizerexclusive#label_data
        """
        return list(self.labels)

    @property
    def label_map(self) -> Dict[str, int]:
        """RETURNS (Dict[str, int]): The label map."""
        return {label: i for i, label in enumerate(self.labels)}

    @property
    def _negative_label(self) -> int:
        """RETURNS (int): Index of the negative label."""
        return len(self.label_data)

    @property
    def _n_labels(self) -> int:
        """RETURNS (int): Number of labels including the negative label."""
        return len(self.label_data) + 1

    def predict(self, docs: Iterable[Doc]):
        """Apply the pipeline's model to a batch of docs, without modifying them.

        docs (Iterable[Doc]): The documents to predict.
        RETURNS: The models prediction for each document.

        DOCS: https://spacy.io/api/spancategorizerexclusive#predict
        """
        indices = self.suggester(docs, ops=self.model.ops)
        scores = self.model.predict((docs, indices))  # type: ignore
        return indices, scores

    def set_candidates(
        self, docs: Iterable[Doc], *, candidates_key: str = "candidates"
    ) -> None:
        """Use the spancat suggester to add a list of span candidates to a
        list of docs. Intended to be used for debugging purposes.

        docs (Iterable[Doc]): The documents to modify.
        candidates_key (str): Key of the Doc.spans dict to save the
            candidate spans under.

        DOCS: https://spacy.io/api/spancategorizerexclusive#set_candidates
        """
        suggester_output = self.suggester(docs, ops=self.model.ops)

        for candidates, doc in zip(suggester_output, docs):  # type: ignore
            doc.spans[candidates_key] = []
            for index in candidates.dataXd:
                doc.spans[candidates_key].append(doc[index[0] : index[1]])

    def set_annotations(self, docs: Iterable[Doc], indices_scores) -> None:
        """Modify a batch of Doc objects, using pre-computed scores.

        docs (Iterable[Doc]): The documents to modify.
        scores: The scores to set, produced by SpanCategorizerExclusive.predict.

        DOCS: https://spacy.io/api/spancategorizerexclusive#set_annotations
        """
        allow_overlap = cast(bool, self.cfg["allow_overlap"])
        labels = self.labels
        indices, scores = indices_scores
        offset = 0
        for i, doc in enumerate(docs):
            indices_i = indices[i].dataXd
            doc.spans[self.key] = self._make_span_group(
                doc,
                indices_i,
                scores[offset : offset + indices.lengths[i]],
                labels,  # type: ignore[arg-type]
                allow_overlap,
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

        DOCS: https://spacy.io/api/spancategorizerexclusive#update
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

        DOCS: https://spacy.io/api/spancategorizerexclusive#get_loss
        """
        spans, scores = spans_scores
        spans = Ragged(
            self.model.ops.to_numpy(spans.data), self.model.ops.to_numpy(spans.lengths)
        )
        target = numpy.zeros(scores.shape, dtype=scores.dtype)
        # Set negative class as target initially for all samples.
        negative_spans = numpy.ones((scores.shape[0]))
        offset = 0
        for i, eg in enumerate(examples):
            # Map (start, end) offset of spans to the row in the
            # d_scores array, so that we can adjust the gradient
            # for predictions that were in the gold standard.
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
                    k = self.label_map[gold_span.label_]
                    target[row, k] = 1.0
                    # delete negative label target.
                    negative_spans[row] = 0.0
            # The target is a flat array for all docs. Track the position
            # we're at within the flat array.
            offset += spans.lengths[i]
        target = self.model.ops.asarray(target, dtype="f")  # type: ignore
        negative_samples = numpy.nonzero(negative_spans)[0]
        target[negative_samples, self._negative_label] = 1.0  # type: ignore
        d_scores = scores - target
        neg_weight = cast(float, self.cfg["negative_weight"])
        d_scores[negative_samples] *= neg_weight
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

        DOCS: https://spacy.io/api/spancategorizerexclusive#initialize
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
            # + 1 for the "no-label" category
            Y = self.model.ops.alloc2f(spans.dataXd.shape[0], self._n_labels)
            self.model.initialize(X=(docs, spans), Y=Y)
        else:
            # FIXME: Ideally we want to raise an error to avoid implicitly
            # raising it when initializing without examples. For now, we'll just
            # copy over what `spancat` did.
            self.model.initialize()

    def _validate_categories(self, examples: Iterable[Example]):
        # TODO
        pass

    def _get_aligned_spans(self, eg: Example):
        return eg.get_aligned_spans_y2x(
            eg.reference.spans.get(self.key, []), allow_overlap=True
        )

    def _make_span_group(
        self,
        doc: Doc,
        indices: Ints2d,
        scores: Floats2d,
        labels: List[str],
        allow_overlap: bool = True,
    ) -> SpanGroup:
        scores = self.model.ops.to_numpy(scores)
        indices = self.model.ops.to_numpy(indices)
        predicted = scores.argmax(axis=1)

        # Remove samples where the negative label is the argmax
        positive = numpy.where(predicted != self._negative_label)[0]
        predicted = predicted[positive]
        indices = indices[positive]

        # Sort spans according to argmax probability
        if not allow_overlap:
            # Get the probabilities
            argmax_probs = numpy.take_along_axis(
                scores[positive], numpy.expand_dims(predicted, 1), axis=1
            )
            argmax_probs = argmax_probs.squeeze()
            sort_idx = (argmax_probs * -1).argsort()
            predicted = predicted[sort_idx]
            indices = indices[sort_idx]

        seen = Ranges()
        spans = SpanGroup(doc, name=self.key)
        for i in range(len(predicted)):
            label = predicted[i]
            start = indices[i, 0]
            end = indices[i, 1]

            if not allow_overlap:
                if (start, end) in seen:
                    continue
                else:
                    seen.add(start, end)

            spans.append(Span(doc, start, end, label=labels[label]))

        return spans
