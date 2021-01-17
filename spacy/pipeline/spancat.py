from thinc.v2v import Maxout, Affine, Model
from thinc.t2v import Pooling, sum_pool
from thinc.api import layerize, chain
from thinc.misc import LayerNorm, Residual
from .pipes import Pipe
from .._ml import logistic, zero_init, Tok2Vec

spancat_default_config = """
[model]
@architectures = "spacy.SpanCategorizer.v1"
reducer = {"@architectures": "reduce_mean.v1"}
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
DEFAULT_MULTI_TEXTCAT_MODEL = Config().from_str(multi_label_default_config)["model"]



@Language.factory(
    "spancat",
    assigns=["doc.spans"],
    default_config={},
    default_score_weights={},
)
def make_spancat(
    nlp: Language,
    name: str,
    suggester: Callable[List[Doc], Ragged],
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
        max_positive=max_positive
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

    def predict(self, docs, drop=0.0):
        indices = self.suggester(docs)
        scores = self.model.predict((docs, indices))
        return (indices, scores)

    def set_annotations(self, docs, indices_scores):
        labels = self.labels
        indices, scores = indices_scores
        for i, doc in enumerate(docs):
            doc.spans[self.key] = self._make_span_group(
                doc,
                indices[i].dataXd,
                scores[i].dataXd,
                labels
            )
        return docs

    def update(self, examples, sgd=None, drop=0.0, losses=None):
        if losses is None:
            losses = {}
        losses.setdefault(self.name, 0.0)
        validate_examples(examples, "SpanCategorizer.update")
        self._validate_categories(examples)
        if not any(len(eg.predicted) if eg.predicted else 0 for eg in examples):
            # Handle cases where there are no tokens in any docs.
            return losses
        docs = [eg.predicted for eg in examples]
        spans = self.suggester(docs)
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
            for j, (start, end) in enumerate(spans[i]):
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
        target = model.ops.asarray(target)
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
        nlp: Language=None
    ):
        """Initialize the pipe for training, using data examples if available."""
        subbatch = []
        for eg in get_examples():
            for span in eg.reference.spans[self.key]:
                self.add_label(label)
            if len(subbatch) < 10:
                subbatch.append(eg)
        docs = [eg.x for eg in subbatch]
        Ys = self._get_aligned_spans([eg.y for y in subbatch])
        self.model.initialize((docs, self.suggester(docs)), Ys)

    def _make_span_group(
        self,
        doc: Doc,
        indices: Ints2d,
        scores: Floats2d,
        labels: List[str]
    ):
        spans = SpanGroup(doc, name=self.key)
        for i, (start, end) in enumerate(indices):
            positives = []
            for j, score in enumerate(scores[i]):
                if score >= self.positive:
                    positives.append((score, start, end, labels[j]))
            positives.sort(reverse=True)
            if self.max_positive:
                positives = positives[:self.max_positive]
            for score, start, end, label in positives:
                spans.append(Span(doc, start, end, label=label))
        return spans
