from typing import cast, Any, Callable, Dict, Iterable, List, Optional
from typing import Tuple
from collections import Counter
from itertools import islice
import numpy as np

import srsly
from thinc.api import Config, Model, SequenceCategoricalCrossentropy
from thinc.types import Floats2d, Ints1d, Ints2d

from ._edit_tree_internals.edit_trees import EditTrees
from ._edit_tree_internals.schemas import validate_edit_tree
from .lemmatizer import lemmatizer_score
from .trainable_pipe import TrainablePipe
from ..errors import Errors
from ..language import Language
from ..tokens import Doc
from ..training import Example, validate_examples, validate_get_examples
from ..vocab import Vocab
from .. import util


default_model_config = """
[model]
@architectures = "spacy.Tagger.v2"

[model.tok2vec]
@architectures = "spacy.HashEmbedCNN.v2"
pretrained_vectors = null
width = 96
depth = 4
embed_size = 2000
window_size = 1
maxout_pieces = 3
subword_features = true
"""
DEFAULT_EDIT_TREE_LEMMATIZER_MODEL = Config().from_str(default_model_config)["model"]


@Language.factory(
    "trainable_lemmatizer",
    assigns=["token.lemma"],
    requires=[],
    default_config={
        "model": DEFAULT_EDIT_TREE_LEMMATIZER_MODEL,
        "backoff": "orth",
        "min_tree_freq": 3,
        "overwrite": False,
        "top_k": 1,
        "scorer": {"@scorers": "spacy.lemmatizer_scorer.v1"},
    },
    default_score_weights={"lemma_acc": 1.0},
)
def make_edit_tree_lemmatizer(
    nlp: Language,
    name: str,
    model: Model,
    backoff: Optional[str],
    min_tree_freq: int,
    overwrite: bool,
    top_k: int,
    scorer: Optional[Callable],
):
    """Construct an EditTreeLemmatizer component."""
    return EditTreeLemmatizer(
        nlp.vocab,
        model,
        name,
        backoff=backoff,
        min_tree_freq=min_tree_freq,
        overwrite=overwrite,
        top_k=top_k,
        scorer=scorer,
    )


class EditTreeLemmatizer(TrainablePipe):
    """
    Lemmatizer that lemmatizes each word using a predicted edit tree.
    """

    def __init__(
        self,
        vocab: Vocab,
        model: Model,
        name: str = "trainable_lemmatizer",
        *,
        backoff: Optional[str] = "orth",
        min_tree_freq: int = 3,
        overwrite: bool = False,
        top_k: int = 1,
        scorer: Optional[Callable] = lemmatizer_score,
    ):
        """
        Construct an edit tree lemmatizer.

        backoff (Optional[str]): backoff to use when the predicted edit trees
            are not applicable. Must be an attribute of Token or None (leave the
            lemma unset).
        min_tree_freq (int): prune trees that are applied less than this
            frequency in the training data.
        overwrite (bool): overwrite existing lemma annotations.
        top_k (int): try to apply at most the k most probable edit trees.
        """
        self.vocab = vocab
        self.model = model
        self.name = name
        self.backoff = backoff
        self.min_tree_freq = min_tree_freq
        self.overwrite = overwrite
        self.top_k = top_k

        self.trees = EditTrees(self.vocab.strings)
        self.tree2label: Dict[int, int] = {}

        self.cfg: Dict[str, Any] = {"labels": []}
        self.scorer = scorer

    def get_loss(
        self, examples: Iterable[Example], scores: List[Floats2d]
    ) -> Tuple[float, List[Floats2d]]:
        validate_examples(examples, "EditTreeLemmatizer.get_loss")
        loss_func = SequenceCategoricalCrossentropy(normalize=False, missing_value=-1)

        truths = []
        for eg in examples:
            eg_truths = []
            for (predicted, gold_lemma) in zip(
                eg.predicted, eg.get_aligned("LEMMA", as_string=True)
            ):
                if gold_lemma is None:
                    label = -1
                else:
                    tree_id = self.trees.add(predicted.text, gold_lemma)
                    label = self.tree2label.get(tree_id, 0)
                eg_truths.append(label)

            truths.append(eg_truths)

        d_scores, loss = loss_func(scores, truths)
        if self.model.ops.xp.isnan(loss):
            raise ValueError(Errors.E910.format(name=self.name))

        return float(loss), d_scores

    def predict(self, docs: Iterable[Doc]) -> List[Ints2d]:
        n_docs = len(list(docs))
        if not any(len(doc) for doc in docs):
            # Handle cases where there are no tokens in any docs.
            n_labels = len(self.cfg["labels"])
            guesses: List[Ints2d] = [self.model.ops.alloc2i(0, n_labels) for _ in docs]
            assert len(guesses) == n_docs
            return guesses
        scores = self.model.predict(docs)
        assert len(scores) == n_docs
        guesses = self._scores2guesses(docs, scores)
        assert len(guesses) == n_docs
        return guesses

    def _scores2guesses(self, docs, scores):
        guesses = []
        for doc, doc_scores in zip(docs, scores):
            if self.top_k == 1:
                doc_guesses = doc_scores.argmax(axis=1).reshape(-1, 1)
            else:
                doc_guesses = np.argsort(doc_scores)[..., : -self.top_k - 1 : -1]

            if not isinstance(doc_guesses, np.ndarray):
                doc_guesses = doc_guesses.get()

            doc_compat_guesses = []
            for token, candidates in zip(doc, doc_guesses):
                tree_id = -1
                for candidate in candidates:
                    candidate_tree_id = self.cfg["labels"][candidate]

                    if self.trees.apply(candidate_tree_id, token.text) is not None:
                        tree_id = candidate_tree_id
                        break
                doc_compat_guesses.append(tree_id)

            guesses.append(np.array(doc_compat_guesses))

        return guesses

    def set_annotations(self, docs: Iterable[Doc], batch_tree_ids):
        for i, doc in enumerate(docs):
            doc_tree_ids = batch_tree_ids[i]
            if hasattr(doc_tree_ids, "get"):
                doc_tree_ids = doc_tree_ids.get()
            for j, tree_id in enumerate(doc_tree_ids):
                if self.overwrite or doc[j].lemma == 0:
                    # If no applicable tree could be found during prediction,
                    # the special identifier -1 is used. Otherwise the tree
                    # is guaranteed to be applicable.
                    if tree_id == -1:
                        if self.backoff is not None:
                            doc[j].lemma = getattr(doc[j], self.backoff)
                    else:
                        lemma = self.trees.apply(tree_id, doc[j].text)
                        doc[j].lemma_ = lemma

    @property
    def labels(self) -> Tuple[int, ...]:
        """Returns the labels currently added to the component."""
        return tuple(self.cfg["labels"])

    @property
    def hide_labels(self) -> bool:
        return True

    @property
    def label_data(self) -> Dict:
        trees = []
        for tree_id in range(len(self.trees)):
            tree = self.trees[tree_id]
            if "orig" in tree:
                tree["orig"] = self.vocab.strings[tree["orig"]]
            if "subst" in tree:
                tree["subst"] = self.vocab.strings[tree["subst"]]
            trees.append(tree)
        return dict(trees=trees, labels=tuple(self.cfg["labels"]))

    def initialize(
        self,
        get_examples: Callable[[], Iterable[Example]],
        *,
        nlp: Optional[Language] = None,
        labels: Optional[Dict] = None,
    ):
        validate_get_examples(get_examples, "EditTreeLemmatizer.initialize")

        if labels is None:
            self._labels_from_data(get_examples)
        else:
            self._add_labels(labels)

        # Sample for the model.
        doc_sample = []
        label_sample = []
        for example in islice(get_examples(), 10):
            doc_sample.append(example.x)
            gold_labels: List[List[float]] = []
            for token in example.reference:
                if token.lemma == 0:
                    gold_label = None
                else:
                    gold_label = self._pair2label(token.text, token.lemma_)

                gold_labels.append(
                    [
                        1.0 if label == gold_label else 0.0
                        for label in self.cfg["labels"]
                    ]
                )

            gold_labels = cast(Floats2d, gold_labels)
            label_sample.append(self.model.ops.asarray(gold_labels, dtype="float32"))

        self._require_labels()
        assert len(doc_sample) > 0, Errors.E923.format(name=self.name)
        assert len(label_sample) > 0, Errors.E923.format(name=self.name)

        self.model.initialize(X=doc_sample, Y=label_sample)

    def from_bytes(self, bytes_data, *, exclude=tuple()):
        deserializers = {
            "cfg": lambda b: self.cfg.update(srsly.json_loads(b)),
            "model": lambda b: self.model.from_bytes(b),
            "vocab": lambda b: self.vocab.from_bytes(b, exclude=exclude),
            "trees": lambda b: self.trees.from_bytes(b),
        }

        util.from_bytes(bytes_data, deserializers, exclude)

        return self

    def to_bytes(self, *, exclude=tuple()):
        serializers = {
            "cfg": lambda: srsly.json_dumps(self.cfg),
            "model": lambda: self.model.to_bytes(),
            "vocab": lambda: self.vocab.to_bytes(exclude=exclude),
            "trees": lambda: self.trees.to_bytes(),
        }

        return util.to_bytes(serializers, exclude)

    def to_disk(self, path, exclude=tuple()):
        path = util.ensure_path(path)
        serializers = {
            "cfg": lambda p: srsly.write_json(p, self.cfg),
            "model": lambda p: self.model.to_disk(p),
            "vocab": lambda p: self.vocab.to_disk(p, exclude=exclude),
            "trees": lambda p: self.trees.to_disk(p),
        }
        util.to_disk(path, serializers, exclude)

    def from_disk(self, path, exclude=tuple()):
        def load_model(p):
            try:
                with open(p, "rb") as mfile:
                    self.model.from_bytes(mfile.read())
            except AttributeError:
                raise ValueError(Errors.E149) from None

        deserializers = {
            "cfg": lambda p: self.cfg.update(srsly.read_json(p)),
            "model": load_model,
            "vocab": lambda p: self.vocab.from_disk(p, exclude=exclude),
            "trees": lambda p: self.trees.from_disk(p),
        }

        util.from_disk(path, deserializers, exclude)
        return self

    def _add_labels(self, labels: Dict):
        if "labels" not in labels:
            raise ValueError(Errors.E857.format(name="labels"))
        if "trees" not in labels:
            raise ValueError(Errors.E857.format(name="trees"))

        self.cfg["labels"] = list(labels["labels"])
        trees = []
        for tree in labels["trees"]:
            errors = validate_edit_tree(tree)
            if errors:
                raise ValueError(Errors.E1026.format(errors="\n".join(errors)))

            tree = dict(tree)
            if "orig" in tree:
                tree["orig"] = self.vocab.strings[tree["orig"]]
            if "orig" in tree:
                tree["subst"] = self.vocab.strings[tree["subst"]]

            trees.append(tree)

        self.trees.from_json(trees)

        for label, tree in enumerate(self.labels):
            self.tree2label[tree] = label

    def _labels_from_data(self, get_examples: Callable[[], Iterable[Example]]):
        # Count corpus tree frequencies in ad-hoc storage to avoid cluttering
        # the final pipe/string store.
        vocab = Vocab()
        trees = EditTrees(vocab.strings)
        tree_freqs: Counter = Counter()
        repr_pairs: Dict = {}
        for example in get_examples():
            for token in example.reference:
                if token.lemma != 0:
                    tree_id = trees.add(token.text, token.lemma_)
                    tree_freqs[tree_id] += 1
                    repr_pairs[tree_id] = (token.text, token.lemma_)

        # Construct trees that make the frequency cut-off using representative
        # form - token pairs.
        for tree_id, freq in tree_freqs.items():
            if freq >= self.min_tree_freq:
                form, lemma = repr_pairs[tree_id]
                self._pair2label(form, lemma, add_label=True)

    def _pair2label(self, form, lemma, add_label=False):
        """
        Look up the edit tree identifier for a form/label pair. If the edit
        tree is unknown and "add_label" is set, the edit tree will be added to
        the labels.
        """
        tree_id = self.trees.add(form, lemma)
        if tree_id not in self.tree2label:
            if not add_label:
                return None

            self.tree2label[tree_id] = len(self.cfg["labels"])
            self.cfg["labels"].append(tree_id)
        return self.tree2label[tree_id]
