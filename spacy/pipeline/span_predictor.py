from typing import Iterable, Tuple, Optional, Dict, Callable, Any, List
import warnings

from thinc.types import Floats2d, Floats3d, Ints2d
from thinc.api import Model, Config, Optimizer, CategoricalCrossentropy
from thinc.api import set_dropout_rate, to_categorical
from itertools import islice
from statistics import mean

from .trainable_pipe import TrainablePipe
from ..language import Language
from ..training import Example, validate_examples, validate_get_examples
from ..errors import Errors
from ..scorer import Scorer
from ..tokens import Doc
from ..vocab import Vocab

from ..ml.models.coref_util import (
    MentionClusters,
    DEFAULT_CLUSTER_PREFIX,
    doc2clusters,
)

default_span_predictor_config = """
[model]
@architectures = "spacy.SpanPredictor.v1"
hidden_size = 1024
dist_emb_size = 64

[model.tok2vec]
@architectures = "spacy.Tok2Vec.v2"

[model.tok2vec.embed]
@architectures = "spacy.MultiHashEmbed.v1"
width = 64
rows = [2000, 2000, 1000, 1000, 1000, 1000]
attrs = ["ORTH", "LOWER", "PREFIX", "SUFFIX", "SHAPE", "ID"]
include_static_vectors = false

[model.tok2vec.encode]
@architectures = "spacy.MaxoutWindowEncoder.v2"
width = ${model.tok2vec.embed.width}
window_size = 1
maxout_pieces = 3
depth = 2
"""
DEFAULT_SPAN_PREDICTOR_MODEL = Config().from_str(default_span_predictor_config)["model"]


@Language.factory(
    "span_predictor",
    assigns=["doc.spans"],
    requires=["doc.spans"],
    default_config={
        "model": DEFAULT_SPAN_PREDICTOR_MODEL,
        "input_prefix": "coref_head_clusters",
        "output_prefix": "coref_clusters",
    },
    default_score_weights={"span_accuracy": 1.0},
)
def make_span_predictor(
    nlp: Language,
    name: str,
    model,
    input_prefix: str = "coref_head_clusters",
    output_prefix: str = "coref_clusters",
) -> "SpanPredictor":
    """Create a SpanPredictor component."""
    return SpanPredictor(
        nlp.vocab, model, name, input_prefix=input_prefix, output_prefix=output_prefix
    )


class SpanPredictor(TrainablePipe):
    """Pipeline component to resolve one-token spans to full spans.

    Used in coreference resolution.
    """

    def __init__(
        self,
        vocab: Vocab,
        model: Model,
        name: str = "span_predictor",
        *,
        input_prefix: str = "coref_head_clusters",
        output_prefix: str = "coref_clusters",
    ) -> None:
        self.vocab = vocab
        self.model = model
        self.name = name
        self.input_prefix = input_prefix
        self.output_prefix = output_prefix

        self.cfg = {}

    def predict(self, docs: Iterable[Doc]) -> List[MentionClusters]:
        # for now pretend there's just one doc

        out = []
        for doc in docs:
            # TODO check shape here
            span_scores = self.model.predict([doc])
            if span_scores.size:
                # the information about clustering has to come from the input docs
                # first let's convert the scores to a list of span idxs
                start_scores = span_scores[:, :, 0]
                end_scores = span_scores[:, :, 1]
                starts = start_scores.argmax(axis=1)
                ends = end_scores.argmax(axis=1)

                # TODO check start < end

                # get the old clusters (shape will be preserved)
                clusters = doc2clusters(doc, self.input_prefix)
                cidx = 0
                out_clusters = []
                for cluster in clusters:
                    ncluster = []
                    for mention in cluster:
                        ncluster.append((starts[cidx], ends[cidx]))
                        cidx += 1
                    out_clusters.append(ncluster)
            else:
                out_clusters = []
            out.append(out_clusters)
        return out

    def set_annotations(self, docs: Iterable[Doc], clusters_by_doc) -> None:
        for doc, clusters in zip(docs, clusters_by_doc):
            for ii, cluster in enumerate(clusters):
                spans = [doc[mm[0] : mm[1]] for mm in cluster]
                doc.spans[f"{self.output_prefix}_{ii}"] = spans

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
        """
        if losses is None:
            losses = {}
        losses.setdefault(self.name, 0.0)
        validate_examples(examples, "SpanPredictor.update")
        if not any(len(eg.reference) if eg.reference else 0 for eg in examples):
            # Handle cases where there are no tokens in any docs.
            return losses
        set_dropout_rate(self.model, drop)

        total_loss = 0
        for eg in examples:
            span_scores, backprop = self.model.begin_update([eg.predicted])
            # FIXME, this only happens once in the first 1000 docs of OntoNotes
            # and I'm not sure yet why.
            if span_scores.size:
                loss, d_scores = self.get_loss([eg], span_scores)
                total_loss += loss
                # TODO check shape here
                backprop((d_scores))

        if sgd is not None:
            self.finish_update(sgd)
        losses[self.name] += total_loss
        return losses

    def rehearse(
        self,
        examples: Iterable[Example],
        *,
        drop: float = 0.0,
        sgd: Optional[Optimizer] = None,
        losses: Optional[Dict[str, float]] = None,
    ) -> Dict[str, float]:
        # TODO this should be added later
        raise NotImplementedError(
            Errors.E931.format(
                parent="SpanPredictor", method="add_label", name=self.name
            )
        )

    def add_label(self, label: str) -> int:
        """Technically this method should be implemented from TrainablePipe,
        but it is not relevant for this component.
        """
        raise NotImplementedError(
            Errors.E931.format(
                parent="SpanPredictor", method="add_label", name=self.name
            )
        )

    def get_loss(
        self,
        examples: Iterable[Example],
        span_scores: Floats3d,
    ):
        ops = self.model.ops

        # NOTE This is doing fake batching, and should always get a list of one example
        assert len(examples) == 1, "Only fake batching is supported."
        # starts and ends are gold starts and ends (Ints1d)
        # span_scores is a Floats3d. What are the axes? mention x token x start/end
        for eg in examples:
            starts = []
            ends = []
            for key, sg in eg.reference.spans.items():
                if key.startswith(self.output_prefix):
                    for mention in sg:
                        starts.append(mention.start)
                        ends.append(mention.end)

            starts = self.model.ops.xp.asarray(starts)
            ends = self.model.ops.xp.asarray(ends)
            start_scores = span_scores[:, :, 0]
            end_scores = span_scores[:, :, 1]
            n_classes = start_scores.shape[1]
            start_probs = ops.softmax(start_scores, axis=1)
            end_probs = ops.softmax(end_scores, axis=1)
            start_targets = to_categorical(starts, n_classes)
            end_targets = to_categorical(ends, n_classes)
            start_grads = start_probs - start_targets
            end_grads = end_probs - end_targets
            grads = ops.xp.stack((start_grads, end_grads), axis=2)
            loss = float((grads**2).sum())
        return loss, grads

    def initialize(
        self,
        get_examples: Callable[[], Iterable[Example]],
        *,
        nlp: Optional[Language] = None,
    ) -> None:
        validate_get_examples(get_examples, "SpanPredictor.initialize")

        X = []
        Y = []
        for ex in islice(get_examples(), 2):

            if not ex.predicted.spans:
                # set placeholder for shape inference
                doc = ex.predicted
                assert len(doc) > 2, "Coreference requires at least two tokens"
                doc.spans[f"{self.input_prefix}_0"] = [doc[0:1], doc[1:2]]
            X.append(ex.predicted)
            Y.append(ex.reference)

        assert len(X) > 0, Errors.E923.format(name=self.name)
        self.model.initialize(X=X, Y=Y)

    def score(self, examples, **kwargs):
        """
        Evaluate on reconstructing the correct spans around
        gold heads.
        """
        scores = []
        xp = self.model.ops.xp
        for eg in examples:
            starts = []
            ends = []
            pred_starts = []
            pred_ends = []
            ref = eg.reference
            pred = eg.predicted
            for key, gold_sg in ref.spans.items():
                if key.startswith(self.output_prefix):
                    pred_sg = pred.spans[key]
                    for gold_mention, pred_mention in zip(gold_sg, pred_sg):
                        starts.append(gold_mention.start)
                        ends.append(gold_mention.end)
                        pred_starts.append(pred_mention.start)
                        pred_ends.append(pred_mention.end)

            starts = xp.asarray(starts)
            ends = xp.asarray(ends)
            pred_starts = xp.asarray(pred_starts)
            pred_ends = xp.asarray(pred_ends)
            correct = (starts == pred_starts) * (ends == pred_ends)
            accuracy = correct.mean()
            scores.append(float(accuracy))
        return {"span_accuracy": mean(scores)}
