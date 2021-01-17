import numpy
from typing import List, Callable, Tuple, Optional, Iterable
from thinc.api import Config, Model, get_current_ops, set_dropout_rate
from thinc.types import Ragged, Ints1d, Ints2d, Floats2d
from ..language import Language
from .trainable_pipe import TrainablePipe
from ..tokens import Doc, SpanGroup, Span
from ..training import Example, validate_examples, validate_get_examples
from ..util import registry


spancat_default_config = """
[model]
@architectures = "spacy.SpanCategorizer.v1"
reducer = {"@layers": "reduce_sum.v1"}
scorer = {"@architectures": "spacy.MaxoutLogistic.v1"}

[model.tok2vec]
@architectures = "spacy.Tok2Vec.v1"

[model.tok2vec.embed]
@architectures = "spacy.MultiHashEmbed.v1"
width = 64
rows = [2000, 2000, 1000, 1000, 1000, 1000]
attrs = ["ORTH", "LOWER", "PREFIX", "SUFFIX", "SHAPE", "ID"]
include_static_vectors = false

[model.tok2vec.encode]
@architectures = "spacy.MaxoutWindowEncoder.v1"
width = ${model.tok2vec.embed.width}
window_size = 1
maxout_pieces = 3
depth = 2
"""

DEFAULT_SPANCAT_MODEL = Config().from_str(spancat_default_config)["model"]


@registry.misc("ngram_suggester.v1")
def build_ngram_suggester(sizes: List[int]) -> Ragged:
    """Suggest all spans of the given lengths. Spans are returned as a ragged
    array of integers. The array has two columns, indicating the start and end
    position."""
    def ngram_suggester(docs: List[Doc], *, ops=None) -> Ragged:
        if ops is None:
            ops = get_current_ops()
        spans = []
        lengths = []
        for doc in docs:
            starts = ops.xp.arange(len(doc), dtype="i")
            starts = starts.reshape((-1, 1))
            length = 0
            for size in sizes:
                if size < len(doc):
                    starts_size = starts[:-size]
                    spans.append(ops.xp.hstack((starts_size, starts_size+size)))
                    length += spans[-1].shape[0]
                assert spans[-1].ndim == 2, spans[-1].shape
            lengths.append(length)
        output = Ragged(ops.xp.vstack(spans), ops.asarray(lengths, dtype="i"))
        assert output.dataXd.ndim == 2
        return output
    return ngram_suggester


@Language.factory(
    "spancat",
    assigns=["doc.spans"],
    default_config={
        "threshold": 0.5,
        "spans_key": "spans",
        "max_positive": None,
        "model": DEFAULT_SPANCAT_MODEL,
        "suggester": {
            "@misc": "ngram_suggester.v1",
            "sizes": [1, 2]
        }
    },
    default_score_weights={},
)
def make_spancat(
    nlp: Language,
    name: str,
    suggester: Callable[[List[Doc]], Ragged],
    model: Model[Tuple[List[Doc], Ragged], List[Ragged]],
    spans_key: str,
    threshold: float=0.5,
    max_positive: Optional[int]=None
) -> "SpanCategorizer":
    """Create a SpanCategorizer compoment. The span categorizer consists of two
    components: a suggester function that proposes candidate spans, and a labeller
    model that predicts one or more label for each span.

    suggester (Callable[List[Doc], Ragged]): A function that suggests spans.
        Spans are returned as a ragged array with two integer columns, for the
        start and end positions.
    model (Model[Tuple[List[Doc], Ragged], Floats2d]): A model instance that
        is given a a list of documents and (start, end) indices representing
        candidate span offsets. The model predicts a probability for each category
        for each span.
    spans_key (str): Key of the doc.spans dict to save the spans under. During
        initialization and training, the component will look for spans on the
        reference document under the same key.
    threshold (float): Minimum probability to consider a prediction positive.
        Spans with a positive prediction will be saved on the Doc. Defaults to
        0.5.
    max_positive (int): Maximum number of labels to consider positive per span.
        Defaults to None, indicating no limit.
    """
    return SpanCategorizer(
        nlp.vocab,
        suggester,
        model,
        spans_key,
        threshold=threshold,
        max_positive=max_positive,
        name=name,
    )


class SpanCategorizer(TrainablePipe):
    """Pipeline component to label spans of text."""

    def __init__(
        self,
        vocab,
        suggester,
        model,
        spans_key,
        name="spancat",
        threshold=0.5,
        max_positive=None
    ):
        self.cfg = {
            "labels": [],
            "spans_key": spans_key,
            "threshold": threshold,
            "max_positive": max_positive
        }
        self.vocab = vocab
        self.suggester = suggester
        self.model = model
        self.name = name

    @property
    def key(self):
        return self.cfg["spans_key"]

    def add_label(self, label: str):
        if label not in self.cfg["labels"]:
            self.cfg["labels"].append(label)

    @property
    def labels(self):
        return self.cfg["labels"]

    def predict(self, docs, drop=0.0):
        indices = self.suggester(docs, ops=self.model.ops)
        scores = self.model.predict((docs, indices))
        return (indices, scores)

    def set_annotations(self, docs, indices_scores):
        labels = self.labels
        indices, scores = indices_scores
        offset = 0
        for i, doc in enumerate(docs):
            indices_i = indices[i].dataXd
            doc.spans[self.key] = self._make_span_group(
                doc,
                indices_i,
                scores[offset:offset+indices.lengths[i]],
                labels
            )
            offset += indices.lengths[i]
        return docs

    def update(self, examples, sgd=None, drop=0.0, losses=None, set_annotations=False):
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
        backprop_scores(d_scores)
        if sgd is not None:
            self.finish_update(sgd)
        losses[self.name] += loss
        return losses

    def get_loss(self, examples, spans_scores: Tuple[Ragged, Ragged]):
        spans, scores = spans_scores
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
                start = int(spans_i[j, 0])
                end = int(spans_i[j, 1])
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
        target = self.model.ops.asarray(target, dtype="f")
        # The target will have the values 0 (for untrue predictions) or 1
        # (for true predictions).
        # The scores should be in the range [0, 1].
        # If the prediction is 0.9 and it's true, the gradient
        # will be -0.1 (0.9 - 1.0).
        # If the prediction is 0.9 and it's false, the gradient will be
        # 0.9 (0.9 - 0.0)
        d_scores = (scores - target) / target.shape[0]
        loss = float((d_scores**2).sum())
        return loss, d_scores

    def initialize(
        self,
        get_examples: Callable[[], Iterable[Example]],
        *,
        nlp: Language=None
    ):
        """Initialize the pipe for training, using data examples if available."""
        subbatch = []
        for eg in get_examples():
            for span in eg.reference.spans[self.key]:
                self.add_label(span.label_)
            if len(subbatch) < 10:
                subbatch.append(eg)
        if subbatch:
            docs = [eg.x for eg in subbatch]
            spans = self.suggester(docs)
            Y = self.model.ops.alloc2f(spans.dataXd.shape[0], len(self.labels))
            self.model.initialize(X=(docs, spans), Y=Y)
        else:
            self.model.initialize()

    def _validate_categories(self, examples):
        # TODO
        pass

    def _get_aligned_spans(self, eg):
        return eg.get_aligned_spans_y2x(eg.reference.spans.get(self.key, []))

    def _make_span_group(
        self,
        doc: Doc,
        indices: Ints2d,
        scores: Floats2d,
        labels: List[str]
    ):
        spans = SpanGroup(doc, name=self.key)
        max_positive = self.cfg["max_positive"]
        threshold = self.cfg["threshold"]
        for i in range(indices.shape[0]):
            start = int(indices[i, 0])
            end = int(indices[i, 1])
            positives = []
            for j, score in enumerate(scores[i]):
                if score >= threshold:
                    positives.append((score, start, end, labels[j]))
            positives.sort(reverse=True)
            if max_positive:
                positives = positives[:max_positive]
            for score, start, end, label in positives:
                spans.append(Span(doc, start, end, label=label))
        return spans
