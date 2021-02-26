from typing import Iterable, Tuple, Optional, Dict, Callable, Any

from thinc.api import get_array_module, Model, Optimizer, set_dropout_rate, Config
from itertools import islice

from .trainable_pipe import TrainablePipe
from .coref_er import DEFAULT_MENTIONS
from ..language import Language
from ..training import Example, validate_examples, validate_get_examples
from ..errors import Errors
from ..scorer import Scorer
from ..tokens import Doc
from ..vocab import Vocab


default_config = """
[model]
@architectures = "spacy.Coref.v0"

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
DEFAULT_MODEL = Config().from_str(default_config)["model"]

DEFAULT_CLUSTERS_PREFIX = "coref_cluster"


@Language.factory(
    "coref",
    assigns=[f"doc.spans"],
    requires=["doc.spans"],
    default_config={
        "model": DEFAULT_MODEL,
        "span_mentions": DEFAULT_MENTIONS,
        "span_cluster_prefix": DEFAULT_CLUSTERS_PREFIX,
    },
    default_score_weights={"coref_f": 1.0, "coref_p": None, "coref_r": None},
)
def make_coref(
    nlp: Language,
    name: str,
    model,
    span_mentions: str,
    span_cluster_prefix: str,
) -> "CorefResolution":
    """Create a CorefResolution component. TODO

    model (Model[List[Doc], List[Floats2d]]): A model instance that predicts ...
    threshold (float): Cutoff to consider a prediction "positive".
    """
    return CorefResolution(
        nlp.vocab,
        model,
        name,
        span_mentions=span_mentions,
        span_cluster_prefix=span_cluster_prefix,
    )


class CorefResolution(TrainablePipe):
    """Pipeline component for coreference resolution.

    DOCS: https://spacy.io/api/coref (TODO)
    """

    def __init__(
        self,
        vocab: Vocab,
        model: Model,
        name: str = "coref",
        *,
        span_mentions: str,
        span_cluster_prefix: str,
    ) -> None:
        """Initialize a coreference resolution component.

        vocab (Vocab): The shared vocabulary.
        model (thinc.api.Model): The Thinc Model powering the pipeline component.
        name (str): The component instance name, used to add entries to the
            losses during training.
        span_mentions (str): Key in doc.spans whereh the candidate coref mentions
            are stored in.
        span_cluster_prefix (str): Prefix for the key in doc.spans to store the
            coref clusters in.

        DOCS: https://spacy.io/api/coref#init (TODO)
        """
        self.vocab = vocab
        self.model = model
        self.name = name
        self.span_mentions = span_mentions
        self.span_cluster_prefix = span_cluster_prefix
        self._rehearsal_model = None
        self.cfg = {}

    def predict(self, docs: Iterable[Doc]):
        """Apply the pipeline's model to a batch of docs, without modifying them.
        TODO: write actual algorithm

        docs (Iterable[Doc]): The documents to predict.
        RETURNS: The models prediction for each document.

        DOCS: https://spacy.io/api/coref#predict (TODO)
        """
        clusters_by_doc = []
        for i, doc in enumerate(docs):
            clusters = []
            for span in doc.spans[self.span_mentions]:
                clusters.append([span])
            clusters_by_doc.append(clusters)
        return clusters_by_doc

    def set_annotations(self, docs: Iterable[Doc], clusters_by_doc) -> None:
        """Modify a batch of Doc objects, using pre-computed scores.

        docs (Iterable[Doc]): The documents to modify.
        clusters: The span clusters, produced by CorefResolution.predict.

        DOCS: https://spacy.io/api/coref#set_annotations (TODO)
        """
        if len(docs) != len(clusters_by_doc):
            raise ValueError("Found coref clusters incompatible with the "
                             "documents provided to the 'coref' component. "
                             "This is likely a bug in spaCy.")
        for doc, clusters in zip(docs, clusters_by_doc):
            index = 0
            for cluster in clusters:
                key = self.span_cluster_prefix + str(index)
                if key in doc.spans:
                    raise ValueError(f"Couldn't store the results of {self.name}, as the key "
                                     f"{key} already exists in 'doc.spans'.")
                doc.spans[key] = cluster
                index += 1

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

        DOCS: https://spacy.io/api/coref#update (TODO)
        """
        if losses is None:
            losses = {}
        losses.setdefault(self.name, 0.0)
        validate_examples(examples, "CorefResolution.update")
        if not any(len(eg.predicted) if eg.predicted else 0 for eg in examples):
            # Handle cases where there are no tokens in any docs.
            return losses
        set_dropout_rate(self.model, drop)
        scores, bp_scores = self.model.begin_update([eg.predicted for eg in examples])
        # TODO below
        loss, d_scores = self.get_loss(examples, scores)
        bp_scores(d_scores)
        if sgd is not None:
            self.finish_update(sgd)
        losses[self.name] += loss
        return losses

    def rehearse(
        self,
        examples: Iterable[Example],
        *,
        drop: float = 0.0,
        sgd: Optional[Optimizer] = None,
        losses: Optional[Dict[str, float]] = None,
    ) -> Dict[str, float]:
        """Perform a "rehearsal" update from a batch of data. Rehearsal updates
        teach the current model to make predictions similar to an initial model,
        to try to address the "catastrophic forgetting" problem. This feature is
        experimental.

        examples (Iterable[Example]): A batch of Example objects.
        drop (float): The dropout rate.
        sgd (thinc.api.Optimizer): The optimizer.
        losses (Dict[str, float]): Optional record of the loss during training.
            Updated using the component name as the key.
        RETURNS (Dict[str, float]): The updated losses dictionary.

        DOCS: https://spacy.io/api/coref#rehearse (TODO)
        """
        if losses is not None:
            losses.setdefault(self.name, 0.0)
        if self._rehearsal_model is None:
            return losses
        validate_examples(examples, "CorefResolution.rehearse")
        docs = [eg.predicted for eg in examples]
        if not any(len(doc) for doc in docs):
            # Handle cases where there are no tokens in any docs.
            return losses
        set_dropout_rate(self.model, drop)
        scores, bp_scores = self.model.begin_update(docs)
        # TODO below
        target = self._rehearsal_model(examples)
        gradient = scores - target
        bp_scores(gradient)
        if sgd is not None:
            self.finish_update(sgd)
        if losses is not None:
            losses[self.name] += (gradient ** 2).sum()
        return losses

    def add_label(self, label: str) -> int:
        """Technically this method should be implemented from TrainablePipe,
        but it is not relevant for the coref component.
        """
        raise NotImplementedError(
            Errors.E931.format(
                parent="CorefResolution", method="add_label", name=self.name
            )
        )

    def get_loss(self, examples: Iterable[Example], scores) -> Tuple[float, float]:
        """Find the loss and gradient of loss for the batch of documents and
        their predicted scores.

        examples (Iterable[Examples]): The batch of examples.
        scores: Scores representing the model's predictions.
        RETURNS (Tuple[float, float]): The loss and the gradient.

        DOCS: https://spacy.io/api/coref#get_loss (TODO)
        """
        validate_examples(examples, "CorefResolution.get_loss")
        # TODO
        return float(3.42), float(0.0)

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

        DOCS: https://spacy.io/api/coref#initialize (TODO)
        """
        validate_get_examples(get_examples, "CorefResolution.initialize")
        subbatch = list(islice(get_examples(), 10))
        doc_sample = [eg.reference for eg in subbatch]
        assert len(doc_sample) > 0, Errors.E923.format(name=self.name)
        self.model.initialize(X=doc_sample)

    def score(self, examples: Iterable[Example], **kwargs) -> Dict[str, Any]:
        """Score a batch of examples.

        examples (Iterable[Example]): The examples to score.
        RETURNS (Dict[str, Any]): The scores, produced by Scorer.score_coref.

        DOCS: https://spacy.io/api/coref#score (TODO)
        """
        def clusters_getter(doc, span_key):
            return [spans for name, spans in doc.spans.items() if name.startswith(span_key)]
        validate_examples(examples, "CorefResolution.score")
        kwargs.setdefault("getter", clusters_getter)
        kwargs.setdefault("attr", self.span_cluster_prefix)
        kwargs.setdefault("include_label", False)
        return Scorer.score_clusters(examples, **kwargs)
