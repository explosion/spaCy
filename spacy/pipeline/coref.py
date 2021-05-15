from typing import Iterable, Tuple, Optional, Dict, Callable, Any, List

from thinc.types import Floats2d, Ints2d
from thinc.api import Model, Config, Optimizer, CategoricalCrossentropy
from itertools import islice

from .trainable_pipe import TrainablePipe
from .coref_er import DEFAULT_MENTIONS
from ..language import Language
from ..training import Example, validate_examples, validate_get_examples
from ..errors import Errors
from ..scorer import Scorer
from ..tokens import Doc
from ..vocab import Vocab

from ..ml.models.coref_util import (
    create_gold_scores,
    MentionClusters,
    get_clusters_from_doc,
    logsumexp,
    get_predicted_clusters,
    DEFAULT_CLUSTER_PREFIX,
    doc2clusters,
)


default_config = """
[model]
@architectures = "spacy.Coref.v0"
max_span_width = 20
mention_limit = 3900
dropout = 0.3
hidden = 1000
@get_mentions = "spacy.CorefCandidateGenerator.v0"

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

DEFAULT_CLUSTERS_PREFIX = "coref_clusters"


@Language.factory(
    "coref",
    assigns=["doc.spans"],
    requires=["doc.spans"],
    default_config={
        "model": DEFAULT_MODEL,
        "span_cluster_prefix": DEFAULT_CLUSTER_PREFIX,
    },
    default_score_weights={"coref_f": 1.0, "coref_p": None, "coref_r": None},
)
def make_coref(
    nlp: Language,
    name: str,
    model,
    span_cluster_prefix: str = "coref",
) -> "CoreferenceResolver":
    """Create a CoreferenceResolver component."""

    return CoreferenceResolver(nlp.vocab, model, name, span_cluster_prefix)


class CoreferenceResolver(TrainablePipe):
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
        span_mentions (str): Key in doc.spans where the candidate coref mentions
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
        self.loss = CategoricalCrossentropy()

        self.cfg = {}

    def predict(self, docs: Iterable[Doc]) -> List[MentionClusters]:
        """Apply the pipeline's model to a batch of docs, without modifying them.
        TODO: write actual algorithm

        docs (Iterable[Doc]): The documents to predict.
        RETURNS: The models prediction for each document.

        DOCS: https://spacy.io/api/coref#predict (TODO)
        """
        scores, idxs = self.model.predict(docs)
        # idxs is a list of mentions (start / end idxs)
        # each item in scores includes scores and a mapping from scores to mentions

        xp = self.model.ops.xp

        clusters_by_doc = []
        offset = 0
        for cscores, ant_idxs in scores:
            ll = cscores.shape[0]
            hi = offset + ll

            starts = idxs[offset:hi, 0]
            ends = idxs[offset:hi, 1]

            # need to add the placeholder
            placeholder = self.model.ops.alloc2f(cscores.shape[0], 1)
            cscores = xp.concatenate((placeholder, cscores), 1)

            predicted = get_predicted_clusters(xp, starts, ends, ant_idxs, cscores)
            clusters_by_doc.append(predicted)
        return clusters_by_doc

    def set_annotations(self, docs: Iterable[Doc], clusters_by_doc) -> None:
        """Modify a batch of Doc objects, using pre-computed scores.

        docs (Iterable[Doc]): The documents to modify.
        clusters: The span clusters, produced by CoreferenceResolver.predict.

        DOCS: https://spacy.io/api/coref#set_annotations (TODO)
        """
        if len(docs) != len(clusters_by_doc):
            raise ValueError(
                "Found coref clusters incompatible with the "
                "documents provided to the 'coref' component. "
                "This is likely a bug in spaCy."
            )
        for doc, clusters in zip(docs, clusters_by_doc):
            for ii, cluster in enumerate(clusters):
                key = self.span_cluster_prefix + "_" + str(ii)
                if key in doc.spans:
                    raise ValueError(
                        "Found coref clusters incompatible with the "
                        "documents provided to the 'coref' component. "
                        "This is likely a bug in spaCy."
                    )

                doc.spans[key] = []
                for mention in cluster:
                    doc.spans[key].append(doc[mention[0] : mention[1]])

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
        validate_examples(examples, "CoreferenceResolver.update")
        if not any(len(eg.predicted) if eg.predicted else 0 for eg in examples):
            # Handle cases where there are no tokens in any docs.
            return losses
        set_dropout_rate(self.model, drop)

        inputs = (example.predicted for example in examples)
        preds, backprop = self.model.begin_update(inputs)
        score_matrix, mention_idx = preds
        loss, d_scores = self.get_loss(examples, score_matrix, mention_idx)
        backprop(d_scores)

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
        validate_examples(examples, "CoreferenceResolver.rehearse")
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
                parent="CoreferenceResolver", method="add_label", name=self.name
            )
        )

    def get_loss(
        self,
        examples: Iterable[Example],
        score_matrix: List[Tuple[Floats2d, Ints2d]],
        mention_idx: Ints2d,
    ):
        """Find the loss and gradient of loss for the batch of documents and
        their predicted scores.

        examples (Iterable[Examples]): The batch of examples.
        scores: Scores representing the model's predictions.
        RETURNS (Tuple[float, float]): The loss and the gradient.

        DOCS: https://spacy.io/api/coref#get_loss (TODO)
        """
        ops = self.model.ops
        xp = ops.xp

        offset = 0
        gradients = []
        loss = 0
        for example, (cscores, cidx) in zip(examples, score_matrix):
            # assume cids has absolute mention ids

            ll = cscores.shape[0]
            hi = offset + ll

            clusters = get_clusters_from_doc(example.reference)
            gscores = create_gold_scores(mention_idx[offset:hi], clusters)
            gscores = xp.asarray(gscores)
            top_gscores = xp.take_along_axis(gscores, cidx, axis=1)
            # now add the placeholder
            gold_placeholder = ~top_gscores.any(axis=1).T
            gold_placeholder = xp.expand_dims(gold_placeholder, 1)
            top_gscores = xp.concatenate((gold_placeholder, top_gscores), 1)

            # boolean to float
            top_gscores = ops.asarray2f(top_gscores)

            # add the placeholder to cscores
            placeholder = self.model.ops.alloc2f(ll, 1)
            cscores = xp.concatenate((placeholder, cscores), 1)

            # do softmax to cscores
            cscores = ops.softmax(cscores, axis=1)

            diff = self.loss.get_grad(cscores, top_gscores)
            diff = diff[:, 1:]
            gradients.append((diff, cidx))

            # scalar loss
            # loss += xp.sum(log_norm - log_marg)
            loss += self.loss.get_loss(cscores, top_gscores)
            offset += ll
        return loss, gradients

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
        validate_get_examples(get_examples, "CoreferenceResolver.initialize")
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
            return [
                spans for name, spans in doc.spans.items() if name.startswith(span_key)
            ]

        validate_examples(examples, "CoreferenceResolver.score")
        kwargs.setdefault("getter", clusters_getter)
        kwargs.setdefault("attr", self.span_cluster_prefix)
        kwargs.setdefault("include_label", False)
        return Scorer.score_clusters(examples, **kwargs)


# from ..coref_scorer import Evaluator, get_cluster_info, b_cubed
# TODO consider whether to use this
#    def score(self, examples, **kwargs):
#        """Score a batch of examples."""
#
#        #TODO traditionally coref uses the average of b_cubed, muc, and ceaf.
#        # we need to handle the average ourselves.
#        evaluator = Evaluator(b_cubed)
#
#        for ex in examples:
#            p_clusters = doc2clusters(ex.predicted, self.span_cluster_prefix)
#            g_clusters = doc2clusters(ex.reference, self.span_cluster_prefix)
#
#            cluster_info = get_cluster_info(p_clusters, g_clusters)
#
#            evaluator.update(cluster_info)
#
#        scores ={
#                "coref_f": evaluator.get_f1(),
#                "coref_p": evaluator.get_precision(),
#                "coref_r": evaluator.get_recall(),
#                }
#        return scores
