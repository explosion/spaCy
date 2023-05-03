from functools import partial
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, cast

from thinc.api import Config, Model, Ops, Optimizer, get_current_ops, set_dropout_rate
from thinc.types import Floats2d, Ints1d, Ragged

from spacy.language import Language
from spacy.pipeline.trainable_pipe import TrainablePipe
from spacy.scorer import Scorer
from spacy.tokens import Doc
from spacy.training import Example
from spacy.errors import Errors

from ..util import registry
from .spancat import DEFAULT_SPANS_KEY, Suggester

span_finder_default_config = """
[model]
@architectures = "spacy.SpanFinder.v1"

[model.scorer]
@layers = "spacy.LinearLogistic.v1"
nO = 2

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

DEFAULT_SPAN_FINDER_MODEL = Config().from_str(span_finder_default_config)["model"]
DEFAULT_PREDICTED_KEY = "span_candidates"


@Language.factory(
    "span_finder",
    assigns=["doc.spans"],
    default_config={
        "threshold": 0.5,
        "model": DEFAULT_SPAN_FINDER_MODEL,
        "predicted_key": DEFAULT_PREDICTED_KEY,
        "training_key": DEFAULT_SPANS_KEY,
        # XXX Doesn't 0 seem bad compared to None instead?
        "max_length": None,
        "min_length": None,
        "scorer": {
            "@scorers": "spacy.span_finder_scorer.v1",
            "predicted_key": DEFAULT_PREDICTED_KEY,
            "training_key": DEFAULT_SPANS_KEY,
        },
    },
    default_score_weights={
        f"span_finder_{DEFAULT_PREDICTED_KEY}_f": 1.0,
        f"span_finder_{DEFAULT_PREDICTED_KEY}_p": 0.0,
        f"span_finder_{DEFAULT_PREDICTED_KEY}_r": 0.0,
    },
)
def make_span_finder(
    nlp: Language,
    name: str,
    model: Model[Iterable[Doc], Floats2d],
    scorer: Optional[Callable],
    threshold: float,
    max_length: Optional[int],
    min_length: Optional[int],
    predicted_key: str = DEFAULT_PREDICTED_KEY,
    training_key: str = DEFAULT_SPANS_KEY,
) -> "SpanFinder":
    """Create a SpanFinder component. The component predicts whether a token is
    the start or the end of a potential span.

    model (Model[List[Doc], Floats2d]): A model instance that
        is given a list of documents and predicts a probability for each token.
    threshold (float): Minimum probability to consider a prediction positive.
    predicted_key (str): Name of the span group the predicted spans are saved
        to
    training_key (str): Name of the span group the training spans are read
        from
    max_length (int): Max length of the produced spans (no max limitation when
        set to 0)
    min_length (int): Min length of the produced spans (no min limitation when
        set to 0)
    """
    return SpanFinder(
        nlp,
        model=model,
        threshold=threshold,
        name=name,
        scorer=scorer,
        max_length=max_length,
        min_length=min_length,
        predicted_key=predicted_key,
        training_key=training_key,
    )


@registry.scorers("spacy.span_finder_scorer.v1")
def make_span_finder_scorer(
    predicted_key: str = DEFAULT_PREDICTED_KEY,
    training_key: str = DEFAULT_SPANS_KEY,
):
    return partial(
        span_finder_score, predicted_key=predicted_key, training_key=training_key
    )


def span_finder_score(
    examples: Iterable[Example],
    *,
    predicted_key: str = DEFAULT_PREDICTED_KEY,
    training_key: str = DEFAULT_SPANS_KEY,
    **kwargs,
) -> Dict[str, Any]:
    kwargs = dict(kwargs)
    attr_prefix = "span_finder_"
    kwargs.setdefault("attr", f"{attr_prefix}{predicted_key}")
    kwargs.setdefault("allow_overlap", True)
    kwargs.setdefault(
        "getter", lambda doc, key: doc.spans.get(key[len(attr_prefix) :], [])
    )
    kwargs.setdefault("labeled", False)
    kwargs.setdefault("has_annotation", lambda doc: predicted_key in doc.spans)
    # score_spans can only score spans with the same key in both the reference
    # and predicted docs, so temporarily copy the reference spans from the
    # reference key to the candidates key in the reference docs, restoring the
    # original span groups afterwards
    orig_span_groups = []
    for eg in examples:
        orig_span_groups.append(eg.reference.spans.get(predicted_key))
        if training_key in eg.reference.spans:
            eg.reference.spans[predicted_key] = eg.reference.spans[training_key]
    scores = Scorer.score_spans(examples, **kwargs)
    for orig_span_group, eg in zip(orig_span_groups, examples):
        if orig_span_group is not None:
            eg.reference.spans[predicted_key] = orig_span_group
    return scores


class _MaxInt(int):
    def __le__(self, other):
        return False

    def __lt__(self, other):
        return False

    def __ge__(self, other):
        return True

    def __gt__(self, other):
        return True


class SpanFinder(TrainablePipe):
    """Pipeline that learns span boundaries"""

    def __init__(
        self,
        nlp: Language,
        model: Model[Iterable[Doc], Floats2d],
        name: str = "span_finder",
        *,
        threshold: float = 0.5,
        max_length: Optional[int] = None,
        min_length: Optional[int] = None,
        # XXX I think this is weird and should be just None like in
        scorer: Optional[Callable] = partial(
            span_finder_score,
            predicted_key=DEFAULT_PREDICTED_KEY,
            training_key=DEFAULT_SPANS_KEY,
        ),
        predicted_key: str = DEFAULT_PREDICTED_KEY,
        training_key: str = DEFAULT_SPANS_KEY,
    ) -> None:
        """Initialize the span boundary detector.
        model (thinc.api.Model): The Thinc Model powering the pipeline component.
        name (str): The component instance name, used to add entries to the
            losses during training.
        threshold (float): Minimum probability to consider a prediction
            positive.
        scorer (Optional[Callable]): The scoring method.
        predicted_key (str): Name of the span group the candidate spans are saved to
        training_key (str): Name of the span group the training spans are read from
        max_length (int): Max length of the produced spans (unlimited when set to 0)
        min_length (int): Min length of the produced spans (unlimited when set to 0)
        """
        self.vocab = nlp.vocab
        self.threshold = threshold
        if max_length is None:
            max_length = _MaxInt()
        if min_length is None:
            min_length = 1
        if max_length < 1 or min_length < 1:
            raise ValueError(
                Errors.E1052.format(min_length=min_length, max_length=max_length)
            )
        self.min_length = min_length
        self.max_length = max_length
        self.predicted_key = predicted_key
        self.training_key = training_key
        self.model = model
        self.name = name
        self.scorer = scorer

    def predict(self, docs: Iterable[Doc]):
        """Apply the pipeline's model to a batch of docs, without modifying them.
        docs (Iterable[Doc]): The documents to predict.
        RETURNS: The models prediction for each document.
        """
        scores = self.model.predict(docs)
        return scores

    def set_annotations(self, docs: Iterable[Doc], scores: Floats2d) -> None:
        """Modify a batch of Doc objects, using pre-computed scores.
        docs (Iterable[Doc]): The documents to modify.
        scores: The scores to set, produced by SpanFinder predict method.
        """
        offset = 0
        for i, doc in enumerate(docs):
            doc.spans[self.predicted_key] = []
            starts = []
            ends = []
            doc_scores = scores[offset : offset + len(doc)]

            for token, token_score in zip(doc, doc_scores):
                if token_score[0] >= self.threshold:
                    starts.append(token.i)
                if token_score[1] >= self.threshold:
                    ends.append(token.i)

            for start in starts:
                for end in ends:
                    span_length = end + 1 - start
                    if span_length > self.max_length:
                        break
                    elif self.min_length <= span_length:
                        doc.spans[self.predicted_key].append(doc[start : end + 1])

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
        sgd (Optional[thinc.api.Optimizer]): The optimizer.
        losses (Optional[Dict[str, float]]): Optional record of the loss during training.
            Updated using the component name as the key.
        RETURNS (Dict[str, float]): The updated losses dictionary.
        """
        if losses is None:
            losses = {}
        losses.setdefault(self.name, 0.0)
        predicted = [eg.predicted for eg in examples]
        set_dropout_rate(self.model, drop)
        scores, backprop_scores = self.model.begin_update(predicted)
        loss, d_scores = self.get_loss(examples, scores)
        backprop_scores(d_scores)
        if sgd is not None:
            self.finish_update(sgd)
        losses[self.name] += loss
        return losses

    def get_loss(self, examples, scores) -> Tuple[float, Floats2d]:
        """Find the loss and gradient of loss for the batch of documents and
        their predicted scores.
        examples (Iterable[Examples]): The batch of examples.
        scores: Scores representing the model's predictions.
        RETURNS (Tuple[float, float]): The loss and the gradient.
        """
        reference_truths = self._get_aligned_truth_scores(examples)
        d_scores = scores - self.model.ops.asarray2f(reference_truths)
        loss = float((d_scores**2).sum())
        return loss, d_scores

    def _get_aligned_truth_scores(self, examples) -> List[Tuple[int, int]]:
        """Align scores of the predictions to the references for calculating the loss"""
        # TODO: handle misaligned (None) alignments
        # TODO: handle cases with differing whitespace in texts
        reference_truths = []

        for eg in examples:
            start_indices = set()
            end_indices = set()

            if self.training_key in eg.reference.spans:
                for span in eg.reference.spans[self.training_key]:
                    start_indices.add(eg.reference[span.start].idx)
                    end_indices.add(
                        eg.reference[span.end - 1].idx + len(eg.reference[span.end - 1])
                    )

            for token in eg.predicted:
                reference_truths.append(
                    (
                        1 if token.idx in start_indices else 0,
                        1 if token.idx + len(token) in end_indices else 0,
                    )
                )

        return reference_truths

    def _get_reference(self, docs) -> List[Tuple[int, int]]:
        """Create a reference list of token probabilities"""
        reference_probabilities = []
        for doc in docs:
            start_indices = set()
            end_indices = set()

            if self.training_key in doc.spans:
                for span in doc.spans[self.training_key]:
                    start_indices.add(span.start)
                    end_indices.add(span.end - 1)

            for token in doc:
                reference_probabilities.append(
                    (
                        1 if token.i in start_indices else 0,
                        1 if token.i in end_indices else 0,
                    )
                )

        return reference_probabilities

    def initialize(
        self,
        get_examples: Callable[[], Iterable[Example]],
        *,
        nlp: Optional[Language] = None,
    ) -> None:
        """Initialize the pipe for training, using a representative set
        of data examples.
        get_examples (Callable[[], Iterable[Example]]): Function that
            returns a representative sample of gold-standard Example objects.
        nlp (Optional[Language]): The current nlp object the component is part of.
        """
        subbatch: List[Example] = []

        for eg in get_examples():
            if len(subbatch) < 10:
                subbatch.append(eg)

        if subbatch:
            docs = [eg.reference for eg in subbatch]
            Y = self.model.ops.asarray2f(self._get_reference(docs))
            self.model.initialize(X=docs, Y=Y)
        else:
            self.model.initialize()


@registry.misc("spacy.span_finder_suggester.v1")
def build_span_finder_suggester(candidates_key: str) -> Suggester:
    """Suggest every candidate predicted by the SpanFinder"""

    def span_finder_suggester(
        docs: Iterable[Doc], *, ops: Optional[Ops] = None
    ) -> Ragged:
        if ops is None:
            ops = get_current_ops()
        spans = []
        lengths = []
        for doc in docs:
            length = 0
            if doc.spans[candidates_key]:
                for span in doc.spans[candidates_key]:
                    spans.append([span.start, span.end])
                    length += 1

            lengths.append(length)

        lengths_array = cast(Ints1d, ops.asarray(lengths, dtype="i"))
        if len(spans) > 0:
            output = Ragged(ops.asarray(spans, dtype="i"), lengths_array)
        else:
            output = Ragged(ops.xp.zeros((0, 0), dtype="i"), lengths_array)

        return output

    return span_finder_suggester
