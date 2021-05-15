# cython: infer_types=True, profile=True, binding=True
from typing import Optional, Union, Dict
import srsly
from thinc.api import SequenceCategoricalCrossentropy, Model, Config
from itertools import islice

from ..tokens.doc cimport Doc
from ..vocab cimport Vocab
from ..morphology cimport Morphology

from ..parts_of_speech import IDS as POS_IDS
from ..symbols import POS
from ..language import Language
from ..errors import Errors
from .pipe import deserialize_config
from .tagger import Tagger
from .. import util
from ..scorer import Scorer
from ..training import validate_examples, validate_get_examples


default_model_config = """
[model]
@architectures = "spacy.Tagger.v1"

[model.tok2vec]
@architectures = "spacy.Tok2Vec.v2"

[model.tok2vec.embed]
@architectures = "spacy.CharacterEmbed.v2"
width = 128
rows = 7000
nM = 64
nC = 8
include_static_vectors = false

[model.tok2vec.encode]
@architectures = "spacy.MaxoutWindowEncoder.v2"
width = 128
depth = 4
window_size = 1
maxout_pieces = 3
"""

DEFAULT_MORPH_MODEL = Config().from_str(default_model_config)["model"]


@Language.factory(
    "morphologizer",
    assigns=["token.morph", "token.pos"],
    default_config={"model": DEFAULT_MORPH_MODEL},
    default_score_weights={"pos_acc": 0.5, "morph_acc": 0.5, "morph_per_feat": None},
)
def make_morphologizer(
    nlp: Language,
    model: Model,
    name: str,
):
    return Morphologizer(nlp.vocab, model, name)


class Morphologizer(Tagger):
    POS_FEAT = "POS"

    def __init__(
        self,
        vocab: Vocab,
        model: Model,
        name: str = "morphologizer",
    ):
        """Initialize a morphologizer.

        vocab (Vocab): The shared vocabulary.
        model (thinc.api.Model): The Thinc Model powering the pipeline component.
        name (str): The component instance name, used to add entries to the
            losses during training.

        DOCS: https://spacy.io/api/morphologizer#init
        """
        self.vocab = vocab
        self.model = model
        self.name = name
        self._rehearsal_model = None
        # to be able to set annotations without string operations on labels,
        # store mappings from morph+POS labels to token-level annotations:
        # 1) labels_morph stores a mapping from morph+POS->morph
        # 2) labels_pos stores a mapping from morph+POS->POS
        cfg = {"labels_morph": {}, "labels_pos": {}}
        self.cfg = dict(sorted(cfg.items()))

    @property
    def labels(self):
        """RETURNS (Tuple[str]): The labels currently added to the component."""
        return tuple(self.cfg["labels_morph"].keys())

    @property
    def label_data(self) -> Dict[str, Dict[str, Union[str, float, int, None]]]:
        """A dictionary with all labels data."""
        return {"morph": self.cfg["labels_morph"], "pos": self.cfg["labels_pos"]}

    def add_label(self, label):
        """Add a new label to the pipe.

        label (str): The label to add.
        RETURNS (int): 0 if label is already present, otherwise 1.

        DOCS: https://spacy.io/api/morphologizer#add_label
        """
        if not isinstance(label, str):
            raise ValueError(Errors.E187)
        if label in self.labels:
            return 0
        self._allow_extra_label()
        # normalize label
        norm_label = self.vocab.morphology.normalize_features(label)
        # extract separate POS and morph tags
        label_dict = Morphology.feats_to_dict(label)
        pos = label_dict.get(self.POS_FEAT, "")
        if self.POS_FEAT in label_dict:
            label_dict.pop(self.POS_FEAT)
        # normalize morph string and add to morphology table
        norm_morph = self.vocab.strings[self.vocab.morphology.add(label_dict)]
        # add label mappings
        if norm_label not in self.cfg["labels_morph"]:
            self.cfg["labels_morph"][norm_label] = norm_morph
            self.cfg["labels_pos"][norm_label] = POS_IDS[pos]
        return 1

    def initialize(self, get_examples, *, nlp=None, labels=None):
        """Initialize the pipe for training, using a representative set
        of data examples.

        get_examples (Callable[[], Iterable[Example]]): Function that
            returns a representative sample of gold-standard Example objects.
        nlp (Language): The current nlp object the component is part of.

        DOCS: https://spacy.io/api/morphologizer#initialize
        """
        validate_get_examples(get_examples, "Morphologizer.initialize")
        util.check_lexeme_norms(self.vocab, "morphologizer")
        if labels is not None:
            self.cfg["labels_morph"] = labels["morph"]
            self.cfg["labels_pos"] = labels["pos"]
        else:
            # First, fetch all labels from the data
            for example in get_examples():
                for i, token in enumerate(example.reference):
                    pos = token.pos_
                    # if both are unset, annotation is missing, so do not add
                    # an empty label
                    if pos == "" and not token.has_morph():
                        continue
                    morph = str(token.morph)
                    # create and add the combined morph+POS label
                    morph_dict = Morphology.feats_to_dict(morph)
                    if pos:
                        morph_dict[self.POS_FEAT] = pos
                    norm_label = self.vocab.strings[self.vocab.morphology.add(morph_dict)]
                    # add label->morph and label->POS mappings
                    if norm_label not in self.cfg["labels_morph"]:
                        self.cfg["labels_morph"][norm_label] = morph
                        self.cfg["labels_pos"][norm_label] = POS_IDS[pos]
        if len(self.labels) < 1:
            raise ValueError(Errors.E143.format(name=self.name))
        doc_sample = []
        label_sample = []
        for example in islice(get_examples(), 10):
            gold_array = []
            for i, token in enumerate(example.reference):
                pos = token.pos_
                morph = str(token.morph)
                morph_dict = Morphology.feats_to_dict(morph)
                if pos:
                    morph_dict[self.POS_FEAT] = pos
                norm_label = self.vocab.strings[self.vocab.morphology.add(morph_dict)]
                gold_array.append([1.0 if label == norm_label else 0.0 for label in self.labels])
            doc_sample.append(example.x)
            label_sample.append(self.model.ops.asarray(gold_array, dtype="float32"))
        assert len(doc_sample) > 0, Errors.E923.format(name=self.name)
        assert len(label_sample) > 0, Errors.E923.format(name=self.name)
        self.model.initialize(X=doc_sample, Y=label_sample)

    def set_annotations(self, docs, batch_tag_ids):
        """Modify a batch of documents, using pre-computed scores.

        docs (Iterable[Doc]): The documents to modify.
        batch_tag_ids: The IDs to set, produced by Morphologizer.predict.

        DOCS: https://spacy.io/api/morphologizer#set_annotations
        """
        if isinstance(docs, Doc):
            docs = [docs]
        cdef Doc doc
        cdef Vocab vocab = self.vocab
        for i, doc in enumerate(docs):
            doc_tag_ids = batch_tag_ids[i]
            if hasattr(doc_tag_ids, "get"):
                doc_tag_ids = doc_tag_ids.get()
            for j, tag_id in enumerate(doc_tag_ids):
                morph = self.labels[tag_id]
                doc.c[j].morph = self.vocab.morphology.add(self.cfg["labels_morph"].get(morph, 0))
                doc.c[j].pos = self.cfg["labels_pos"].get(morph, 0)

    def get_loss(self, examples, scores):
        """Find the loss and gradient of loss for the batch of documents and
        their predicted scores.

        examples (Iterable[Examples]): The batch of examples.
        scores: Scores representing the model's predictions.
        RETURNS (Tuple[float, float]): The loss and the gradient.

        DOCS: https://spacy.io/api/morphologizer#get_loss
        """
        validate_examples(examples, "Morphologizer.get_loss")
        loss_func = SequenceCategoricalCrossentropy(names=self.labels, normalize=False)
        truths = []
        for eg in examples:
            eg_truths = []
            pos_tags = eg.get_aligned("POS", as_string=True)
            morphs = eg.get_aligned("MORPH", as_string=True)
            for i in range(len(morphs)):
                pos = pos_tags[i]
                morph = morphs[i]
                # POS may align (same value for multiple tokens) when morph
                # doesn't, so if either is misaligned (None), treat the
                # annotation as missing so that truths doesn't end up with an
                # unknown morph+POS combination
                if pos is None or morph is None:
                    label = None
                # If both are unset, the annotation is missing (empty morph
                # converted from int is "_" rather than "")
                elif pos == "" and morph == "":
                    label = None
                # Otherwise, generate the combined label
                else:
                    label_dict = Morphology.feats_to_dict(morph)
                    if pos:
                        label_dict[self.POS_FEAT] = pos
                    label = self.vocab.strings[self.vocab.morphology.add(label_dict)]
                    # As a fail-safe, skip any unrecognized labels
                    if label not in self.labels:
                        label = None
                eg_truths.append(label)
            truths.append(eg_truths)
        d_scores, loss = loss_func(scores, truths)
        if self.model.ops.xp.isnan(loss):
            raise ValueError(Errors.E910.format(name=self.name))
        return float(loss), d_scores

    def score(self, examples, **kwargs):
        """Score a batch of examples.

        examples (Iterable[Example]): The examples to score.
        RETURNS (Dict[str, Any]): The scores, produced by
            Scorer.score_token_attr for the attributes "pos" and "morph" and
            Scorer.score_token_attr_per_feat for the attribute "morph".

        DOCS: https://spacy.io/api/morphologizer#score
        """
        def morph_key_getter(token, attr):
            return getattr(token, attr).key

        validate_examples(examples, "Morphologizer.score")
        results = {}
        results.update(Scorer.score_token_attr(examples, "pos", **kwargs))
        results.update(Scorer.score_token_attr(examples, "morph", getter=morph_key_getter, **kwargs))
        results.update(Scorer.score_token_attr_per_feat(examples,
            "morph", getter=morph_key_getter, **kwargs))
        return results
