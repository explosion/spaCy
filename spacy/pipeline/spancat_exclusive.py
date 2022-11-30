from typing import Callable, Dict, Iterable, List, Optional, Tuple, cast
from dataclasses import dataclass

import numpy
from thinc.api import Config, Model
from thinc.types import Floats2d, Ints2d, Ragged

from ..language import Language
from ..tokens import Doc, Span, SpanGroup
from ..training import Example
from ..vocab import Vocab
from .spancat import spancat_score, Suggester
from .spancat import SpanCategorizer


spancat_excl_default_config = """
[model]
@architectures = "spacy.SpanCategorizer.v1"
scorer = {"@layers": "Softmax.v2"}

[model.scorer.init_W]
@initializers = "zero_init.v1"

[model.scorer.init_b]
@initializers = "zero_init.v1"

[model.reducer]
@layers = spacy.mean_max_reducer.v1
hidden_size = 128

[model.tok2vec]
@architectures = "spacy.Tok2Vec.v2"
[model.tok2vec.embed]
@architectures = "spacy.MultiHashEmbed.v1"
width = 96
rows = [5000, 1000, 2500, 1000]
attrs = ["NORM", "PREFIX", "SUFFIX", "SHAPE"]
include_static_vectors = false

[model.tok2vec.encode]
@architectures = "spacy.MaxoutWindowEncoder.v2"
width = ${model.tok2vec.embed.width}
window_size = 1
maxout_pieces = 3
depth = 4
"""

DEFAULT_EXCL_SPANCAT_MODEL = Config().from_str(spancat_excl_default_config)["model"]


@Language.factory(
    "spancat_exclusive",
    assigns=["doc.spans"],
    default_config={
        "spans_key": "sc",
        "model": DEFAULT_EXCL_SPANCAT_MODEL,
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
) -> "Exclusive_SpanCategorizer":
    """Create a SpanCategorizerExclusive component. The span categorizer consists of two
    parts: a suggester function that proposes candidate spans, and a labeler
    model that predicts a maximum of one label for each span.

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
    negative_weight (float): Multiplier for the loss terms.
        Can be used to downweight the negative samples if there are too many.
    allow_overlap (bool): If True the data is assumed to
        contain overlapping spans.
    """
    return Exclusive_SpanCategorizer(
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
    Helper class to avoid storing overlapping spans.
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


class Exclusive_SpanCategorizer(SpanCategorizer):
    """Pipeline component to label spans with exclusive classes.

    DOCS: https://spacy.io/api/spancatcategorizer
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

        DOCS: https://spacy.io/api/spancatcategorizer#init
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

    def set_annotations(self, docs: Iterable[Doc], indices_scores) -> None:
        """Modify a batch of Doc objects, using pre-computed scores.

        docs (Iterable[Doc]): The documents to modify.
        scores: The scores to set, produced by SpanCategorizerExclusive.predict.

        DOCS: https://spacy.io/api/spancatcategorizer#set_annotations
        """
        allow_overlap = cast(bool, self.cfg["allow_overlap"])
        labels = list(self.labels)
        indices, scores = indices_scores
        offset = 0
        for i, doc in enumerate(docs):
            indices_i = indices[i].dataXd
            doc.spans[self.key] = self._make_span_group(
                doc,
                indices_i,
                scores[offset : offset + indices.lengths[i]],
                labels,
                allow_overlap,
            )
            offset += indices.lengths[i]

    def get_loss(
        self, examples: Iterable[Example], spans_scores: Tuple[Ragged, Floats2d]
    ) -> Tuple[float, float]:
        """Find the loss and gradient of loss for the batch of documents and
        their predicted scores.

        examples (Iterable[Examples]): The batch of examples.
        spans_scores: Scores representing the model's predictions.
        RETURNS (Tuple[float, float]): The loss and the gradient.

        DOCS: https://spacy.io/api/spancatcategorizer#get_loss
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
        if neg_weight != 1.0:
            d_scores[negative_samples] *= neg_weight
        loss = float((d_scores**2).sum())
        return loss, d_scores

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