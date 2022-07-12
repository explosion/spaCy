from typing import Iterable, Tuple, Optional, Dict, Callable, Any, List
import warnings

from thinc.types import Floats2d, Floats3d, Ints2d
from thinc.api import Model, Config, Optimizer, CategoricalCrossentropy
from thinc.api import set_dropout_rate, to_categorical
from itertools import islice
import srsly

from .trainable_pipe import TrainablePipe
from ..language import Language
from ..training import Example, validate_examples, validate_get_examples
from ..errors import Errors
from ..scorer import Scorer, doc2clusters
from ..tokens import Doc
from ..vocab import Vocab
from ..util import registry, from_bytes, from_disk

from ..ml.models.coref_util import (
    MentionClusters,
    DEFAULT_CLUSTER_PREFIX,
)

default_span_predictor_config = """
[model]
@architectures = "spacy.SpanPredictor.v1"
hidden_size = 1024
distance_embedding_size = 64
conv_channels = 4
window_size = 1
max_distance = 128
prefix = "coref_head_clusters"

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


def span_predictor_scorer(examples: Iterable[Example], **kwargs) -> Dict[str, Any]:
    return Scorer.score_span_predictions(examples, **kwargs)


@registry.scorers("spacy.span_predictor_scorer.v1")
def make_span_predictor_scorer():
    return span_predictor_scorer


@Language.factory(
    "span_predictor",
    assigns=["doc.spans"],
    requires=["doc.spans"],
    default_config={
        "model": DEFAULT_SPAN_PREDICTOR_MODEL,
        "input_prefix": "coref_head_clusters",
        "output_prefix": "coref_clusters",
        "scorer": {"@scorers": "spacy.span_predictor_scorer.v1"},
    },
    default_score_weights={"span_accuracy": 1.0},
)
def make_span_predictor(
    nlp: Language,
    name: str,
    model,
    input_prefix: str = "coref_head_clusters",
    output_prefix: str = "coref_clusters",
    scorer: Optional[Callable] = span_predictor_scorer,
) -> "SpanPredictor":
    """Create a SpanPredictor component."""
    return SpanPredictor(
        nlp.vocab,
        model,
        name,
        input_prefix=input_prefix,
        output_prefix=output_prefix,
        scorer=scorer,
    )


class SpanPredictor(TrainablePipe):
    """Pipeline component to resolve one-token spans to full spans.

    Used in coreference resolution.

    DOCS: https://spacy.io/api/span_predictor
    """

    def __init__(
        self,
        vocab: Vocab,
        model: Model,
        name: str = "span_predictor",
        *,
        input_prefix: str = "coref_head_clusters",
        output_prefix: str = "coref_clusters",
        scorer: Optional[Callable] = span_predictor_scorer,
    ) -> None:
        self.vocab = vocab
        self.model = model
        self.name = name
        self.input_prefix = input_prefix
        self.output_prefix = output_prefix

        self.scorer = scorer
        self.cfg: Dict[str, Any] = {
            "output_prefix": output_prefix,
        }

    def predict(self, docs: Iterable[Doc]) -> List[MentionClusters]:
        """Apply the pipeline's model to a batch of docs, without modifying them.
        Return the list of predicted span clusters.

        docs (Iterable[Doc]): The documents to predict.
        RETURNS (List[MentionClusters]): The model's prediction for each document.

        DOCS: https://spacy.io/api/span_predictor#predict
        """
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
        """Modify a batch of Doc objects, using pre-computed scores.

        docs (Iterable[Doc]): The documents to modify.
        clusters: The span clusters, produced by SpanPredictor.predict.

        DOCS: https://spacy.io/api/span_predictor#set_annotations
        """
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

        examples (Iterable[Example]): A batch of Example objects.
        drop (float): The dropout rate.
        sgd (thinc.api.Optimizer): The optimizer.
        losses (Dict[str, float]): Optional record of the loss during training.
            Updated using the component name as the key.
        RETURNS (Dict[str, float]): The updated losses dictionary.

        DOCS: https://spacy.io/api/span_predictor#update
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
            if eg.x.text != eg.y.text:
                # TODO assign error number
                raise ValueError(
                    """Text, including whitespace, must match between reference and
                    predicted docs in span predictor training.
                    """
                )
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
        """Find the loss and gradient of loss for the batch of documents and
        their predicted scores.

        examples (Iterable[Examples]): The batch of examples.
        scores: Scores representing the model's predictions.
        RETURNS (Tuple[float, float]): The loss and the gradient.

        DOCS: https://spacy.io/api/span_predictor#get_loss
        """
        ops = self.model.ops

        # NOTE This is doing fake batching, and should always get a list of one example
        assert len(list(examples)) == 1, "Only fake batching is supported."
        # starts and ends are gold starts and ends (Ints1d)
        # span_scores is a Floats3d. What are the axes? mention x token x start/end
        for eg in examples:
            starts = []
            ends = []
            keeps = []
            sidx = 0
            for key, sg in eg.reference.spans.items():
                if key.startswith(self.output_prefix):
                    for ii, mention in enumerate(sg):
                        sidx += 1
                        # convert to span in pred
                        sch, ech = (mention.start_char, mention.end_char)
                        span = eg.predicted.char_span(sch, ech)
                        # TODO add to errors.py
                        if span is None:
                            warnings.warn("Could not align gold span in span predictor, skipping")
                            continue
                        starts.append(span.start)
                        ends.append(span.end)
                        keeps.append(sidx - 1)

            starts = self.model.ops.xp.asarray(starts)
            ends = self.model.ops.xp.asarray(ends)
            start_scores = span_scores[:, :, 0][keeps]
            end_scores = span_scores[:, :, 1][keeps]


            n_classes = start_scores.shape[1]
            start_probs = ops.softmax(start_scores, axis=1)
            end_probs = ops.softmax(end_scores, axis=1)
            start_targets = to_categorical(starts, n_classes)
            end_targets = to_categorical(ends, n_classes)
            start_grads = start_probs - start_targets
            end_grads = end_probs - end_targets
            # now return to original shape, with 0s
            final_start_grads = ops.alloc2f(*span_scores[:, :, 0].shape)
            final_start_grads[keeps] = start_grads
            final_end_grads = ops.alloc2f(*final_start_grads.shape)
            final_end_grads[keeps] = end_grads
            # XXX Note this only works with fake batching
            grads = ops.xp.stack((final_start_grads, final_end_grads), axis=2)

            loss = float((grads**2).sum())
        return loss, grads

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
        nlp (Language): The current nlp object the component is part of.

        DOCS: https://spacy.io/api/span_predictor#initialize
        """
        validate_get_examples(get_examples, "SpanPredictor.initialize")

        X = []
        Y = []
        for ex in islice(get_examples(), 2):

            if not ex.predicted.spans:
                # set placeholder for shape inference
                doc = ex.predicted
                # TODO should be able to check if there are some valid docs in the batch
                assert len(doc) > 2, "Coreference requires at least two tokens"
                doc.spans[f"{self.input_prefix}_0"] = [doc[0:1], doc[1:2]]
            X.append(ex.predicted)
            Y.append(ex.reference)

        assert len(X) > 0, Errors.E923.format(name=self.name)
        self.model.initialize(X=X, Y=Y)

        # Store the input dimensionality. nI and nO are not stored explicitly
        # for PyTorch models. This makes it tricky to reconstruct the model
        # during deserialization. So, besides storing the labels, we also
        # store the number of inputs.
        span_predictor = self.model.get_ref("span_predictor")
        self.cfg["nI"] = span_predictor.get_dim("nI")

    def from_bytes(self, bytes_data, *, exclude=tuple()):
        deserializers = {
            "cfg": lambda b: self.cfg.update(srsly.json_loads(b)),
            "vocab": lambda b: self.vocab.from_bytes(b, exclude=exclude),
        }
        from_bytes(bytes_data, deserializers, exclude)

        self._initialize_from_disk()

        model_deserializers = {
            "model": lambda b: self.model.from_bytes(b),
        }
        from_bytes(bytes_data, model_deserializers, exclude)

        return self

    def from_disk(self, path, exclude=tuple()):
        def load_model(p):
            try:
                with open(p, "rb") as mfile:
                    self.model.from_bytes(mfile.read())
            except AttributeError:
                raise ValueError(Errors.E149) from None

        deserializers = {
            "cfg": lambda p: self.cfg.update(srsly.read_json(p)),
            "vocab": lambda p: self.vocab.from_disk(p, exclude=exclude),
        }
        from_disk(path, deserializers, exclude)

        self._initialize_from_disk()

        model_deserializers = {
            "model": load_model,
        }
        from_disk(path, model_deserializers, exclude)

        return self

    def _initialize_from_disk(self):
        # The PyTorch model is constructed lazily, so we need to
        # explicitly initialize the model before deserialization.
        model = self.model.get_ref("span_predictor")
        if model.has_dim("nI") is None:
            model.set_dim("nI", self.cfg["nI"])
        self.model.initialize()
