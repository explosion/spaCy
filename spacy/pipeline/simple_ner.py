from typing import List, Iterable, Optional, Dict, Tuple, Callable
from thinc.types import Floats2d
from thinc.api import SequenceCategoricalCrossentropy, set_dropout_rate, Model
from thinc.api import Optimizer, Config
from thinc.util import to_numpy

from ..errors import Errors
from ..gold import Example, spans_from_biluo_tags, iob_to_biluo, biluo_to_iob
from ..tokens import Doc
from ..language import Language
from ..vocab import Vocab
from ..scorer import Scorer
from .pipe import Pipe


default_model_config = """
[model]
@architectures = "spacy.BILUOTagger.v1"

[model.tok2vec]
@architectures = "spacy.HashEmbedCNN.v1"
pretrained_vectors = null
width = 128
depth = 4
embed_size = 7000
window_size = 1
maxout_pieces = 3
subword_features = true
"""
DEFAULT_SIMPLE_NER_MODEL = Config().from_str(default_model_config)["model"]


@Language.factory(
    "simple_ner",
    assigns=["doc.ents"],
    default_config={"labels": [], "model": DEFAULT_SIMPLE_NER_MODEL},
    scores=["ents_p", "ents_r", "ents_f", "ents_per_type"],
    default_score_weights={"ents_f": 1.0, "ents_p": 0.0, "ents_r": 0.0},
)
def make_simple_ner(
    nlp: Language, name: str, model: Model, labels: Iterable[str]
) -> "SimpleNER":
    return SimpleNER(nlp.vocab, model, name, labels=labels)


class SimpleNER(Pipe):
    """Named entity recognition with a tagging model. The model should include
    validity constraints to ensure that only valid tag sequences are returned."""

    def __init__(
        self,
        vocab: Vocab,
        model: Model,
        name: str = "simple_ner",
        *,
        labels: Iterable[str],
    ) -> None:
        self.vocab = vocab
        self.model = model
        self.name = name
        self.cfg = {"labels": []}
        for label in labels:
            self.add_label(label)
        self.loss_func = SequenceCategoricalCrossentropy(
            names=self.get_tag_names(), normalize=True, missing_value=None
        )
        assert self.model is not None

    @property
    def is_biluo(self) -> bool:
        return self.model.name.startswith("biluo")

    @property
    def labels(self) -> Tuple[str]:
        return tuple(self.cfg["labels"])

    def add_label(self, label: str) -> None:
        """Add a new label to the pipe.
        label (str): The label to add.
        DOCS: https://spacy.io/api/simplener#add_label
        """
        if not isinstance(label, str):
            raise ValueError(Errors.E187)
        if label not in self.labels:
            self.cfg["labels"].append(label)
            self.vocab.strings.add(label)

    def get_tag_names(self) -> List[str]:
        if self.is_biluo:
            return (
                [f"B-{label}" for label in self.labels]
                + [f"I-{label}" for label in self.labels]
                + [f"L-{label}" for label in self.labels]
                + [f"U-{label}" for label in self.labels]
                + ["O"]
            )
        else:
            return (
                [f"B-{label}" for label in self.labels]
                + [f"I-{label}" for label in self.labels]
                + ["O"]
            )

    def predict(self, docs: List[Doc]) -> List[Floats2d]:
        scores = self.model.predict(docs)
        return scores

    def set_annotations(self, docs: List[Doc], scores: List[Floats2d]) -> None:
        """Set entities on a batch of documents from a batch of scores."""
        tag_names = self.get_tag_names()
        for i, doc in enumerate(docs):
            actions = to_numpy(scores[i].argmax(axis=1))
            tags = [tag_names[actions[j]] for j in range(len(doc))]
            if not self.is_biluo:
                tags = iob_to_biluo(tags)
            doc.ents = spans_from_biluo_tags(doc, tags)

    def update(
        self,
        examples: List[Example],
        *,
        set_annotations: bool = False,
        drop: float = 0.0,
        sgd: Optional[Optimizer] = None,
        losses: Optional[Dict[str, float]] = None,
    ) -> Dict[str, float]:
        if losses is None:
            losses = {}
        losses.setdefault("ner", 0.0)
        if not any(_has_ner(eg) for eg in examples):
            return losses
        docs = [eg.predicted for eg in examples]
        set_dropout_rate(self.model, drop)
        scores, bp_scores = self.model.begin_update(docs)
        loss, d_scores = self.get_loss(examples, scores)
        bp_scores(d_scores)
        if set_annotations:
            self.set_annotations(docs, scores)
        if sgd is not None:
            self.model.finish_update(sgd)
        losses["ner"] += loss
        return losses

    def get_loss(self, examples: List[Example], scores) -> Tuple[List[Floats2d], float]:
        truths = []
        for eg in examples:
            tags = eg.get_aligned_ner()
            gold_tags = [(tag if tag != "-" else None) for tag in tags]
            if not self.is_biluo:
                gold_tags = biluo_to_iob(gold_tags)
            truths.append(gold_tags)
        for i in range(len(scores)):
            if len(scores[i]) != len(truths[i]):
                raise ValueError(
                    f"Mismatched output and gold sizes.\n"
                    f"Output: {len(scores[i])}, gold: {len(truths[i])}."
                    f"Input: {len(examples[i].doc)}"
                )
        d_scores, loss = self.loss_func(scores, truths)
        return loss, d_scores

    def begin_training(
        self,
        get_examples: Callable,
        pipeline: Optional[List[Tuple[str, Callable[[Doc], Doc]]]] = None,
        sgd: Optional[Optimizer] = None,
    ):
        if not hasattr(get_examples, "__call__"):
            gold_tuples = get_examples
            get_examples = lambda: gold_tuples
        for label in _get_labels(get_examples()):
            self.add_label(label)
        labels = self.labels
        n_actions = self.model.attrs["get_num_actions"](len(labels))
        self.model.set_dim("nO", n_actions)
        self.model.initialize()
        if pipeline is not None:
            self.init_multitask_objectives(get_examples, pipeline, sgd=sgd, **self.cfg)
        self.loss_func = SequenceCategoricalCrossentropy(
            names=self.get_tag_names(), normalize=True, missing_value=None
        )
        return sgd

    def init_multitask_objectives(self, *args, **kwargs):
        pass

    def score(self, examples, **kwargs):
        return Scorer.score_spans(examples, "ents", **kwargs)


def _has_ner(example: Example) -> bool:
    for ner_tag in example.get_aligned_ner():
        if ner_tag != "-" and ner_tag is not None:
            return True
    else:
        return False


def _get_labels(examples: List[Example]) -> List[str]:
    labels = set()
    for eg in examples:
        for ner_tag in eg.get_aligned("ENT_TYPE", as_string=True):
            if ner_tag != "O" and ner_tag != "-":
                labels.add(ner_tag)
    return list(sorted(labels))
