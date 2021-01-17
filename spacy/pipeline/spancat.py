from thinc.v2v import Maxout, Affine, Model
from thinc.t2v import Pooling, sum_pool
from thinc.api import layerize, chain
from thinc.misc import LayerNorm, Residual
from .pipes import Pipe
from .._ml import logistic, zero_init, Tok2Vec


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
    model (Model[Tuple[List[Doc], Ragged], Ragged]): A model instance that
        is given a a list of documents and (start, end) indices representing
        candidate span offsets. The model predicts a score for each category
        for each span.
    spans_key (str): Key of the doc.spans dict to save the spans under. During
        initialization and training, the component will look for spans on the
        reference document under the same key.
    threshold (float): 
    max_positive (int):
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
        annotation_setter,
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
            losses = {self.name: 0.0}
        set_dropout_rate(self.model, drop)
        docs = [example.x for example in examples]
        spans = self.suggester(docs)
        spans_scores, backprop_scores = self.model((docs, spans))
        d_scores = self.get_loss(examples, spans_scores)
        backprop_scores(d_scores)
        return losses

    def get_loss(self, examples, spans_scores):
        """Predict what % of a span's tokens are in a
        gold-standard span of a given type, in order to give partial credit"""
        # TODO: This is almost surely all wrong? It's cut and paste from the
        # previous code.
        spans, scores = spans_scores
        token_label_matrix = _get_token_label_matrix(
            [self._get_aligned_spans(eg) for eg in examples],
            [len(eg.x) for eg in examples],
            self.labels
        )
        d_scores = numpy.zeros(scores.shape, dtype=scores.dtype)
        for i, (start, end) in enumerate(spans):
            target = token_label_matrix[start:end].sum(axis=0)
            d_scores[i] = scores - target
        return self.model.ops.asarray(d_scores)

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
                spans.append(Span(doc, start, end, label))
        return spans


def _get_token_label_matrix(gold_phrases, lengths, labels):
    """Figure out how each token should be labelled w.r.t. some gold-standard
    spans, where the labels indicate whether that token is part of the span."""
    output = numpy.zeros((sum(lengths), len(labels)), dtype="i")
    label2class = {label: i for i, label in enumerate(labels)}
    offset = 0
    for doc_phrases, length in gold_phrases:
        for phrase in phrases:
            clas = label2class[phrase.label_]
            for i in range(phrase.start, phrase.end):
                output[offset + i, clas] = 1
        offset += length
    return output

"""
    def get_spans(self, docs):
        if self.span_getter is not None:
            return self.span_getter(docs)
        spans = []
        offset = 0
        for doc in docs:
            spans.extend(_get_all_spans(len(doc), self.max_length, offset=offset))
            offset += len(doc)
        return spans


        backprop_scores(d_scores)

        for indices, starts, length in _batch_spans_by_length(spans):
            X = _get_span_batch(tokvecs, starts, length)
            Y, backprop = self.model.spans2scores.begin_update(X, drop=drop)
            dY = self.get_loss((indices, Y), token_label_matrix)
            dX = backprop(dY, sgd=get_grads)
            for i, start in enumerate(starts):
                d_tokvecs[start : start + length] += dX[i]
            losses[self.name] += (dY ** 2).sum()
        backprop_tokvecs(d_tokvecs, sgd=get_grads)
        if sgd is not None:
            for key, (W, dW) in grads.items():
                sgd(W, dW, key=key)
        return losses
"""
