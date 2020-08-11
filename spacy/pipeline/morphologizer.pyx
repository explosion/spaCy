# cython: infer_types=True, profile=True, binding=True
from typing import Optional
import srsly
from thinc.api import SequenceCategoricalCrossentropy, Model, Config

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
from ..gold import validate_examples


default_model_config = """
[model]
@architectures = "spacy.Tagger.v1"

[model.tok2vec]
@architectures = "spacy.Tok2Vec.v1"

[model.tok2vec.embed]
@architectures = "spacy.CharacterEmbed.v1"
width = 128
rows = 7000
nM = 64
nC = 8

[model.tok2vec.encode]
@architectures = "spacy.MaxoutWindowEncoder.v1"
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
    scores=["pos_acc", "morph_acc", "morph_per_feat"],
    default_score_weights={"pos_acc": 0.5, "morph_acc": 0.5},
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
        *,
        labels_morph: Optional[dict] = None,
        labels_pos: Optional[dict] = None,
    ):
        """Initialize a morphologizer.

        vocab (Vocab): The shared vocabulary.
        model (thinc.api.Model): The Thinc Model powering the pipeline component.
        name (str): The component instance name, used to add entries to the
            losses during training.
        labels_morph (dict): Mapping of morph + POS tags to morph labels.
        labels_pos (dict): Mapping of morph + POS tags to POS tags.

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
        cfg = {"labels_morph": labels_morph or {}, "labels_pos": labels_pos or {}}
        self.cfg = dict(sorted(cfg.items()))
        # add mappings for empty morph
        self.cfg["labels_morph"][Morphology.EMPTY_MORPH] = Morphology.EMPTY_MORPH
        self.cfg["labels_pos"][Morphology.EMPTY_MORPH] = POS_IDS[""]

    @property
    def labels(self):
        """RETURNS (Tuple[str]): The labels currently added to the component."""
        return tuple(self.cfg["labels_morph"].keys())

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

    def begin_training(self, get_examples, *, pipeline=None, sgd=None):
        """Initialize the pipe for training, using data examples if available.

        get_examples (Callable[[], Iterable[Example]]): Optional function that
            returns gold-standard Example objects.
        pipeline (List[Tuple[str, Callable]]): Optional list of pipeline
            components that this component is part of. Corresponds to
            nlp.pipeline.
        sgd (thinc.api.Optimizer): Optional optimizer. Will be created with
            create_optimizer if it doesn't exist.
        RETURNS (thinc.api.Optimizer): The optimizer.

        DOCS: https://spacy.io/api/morphologizer#begin_training
        """
        if not hasattr(get_examples, "__call__"):
            err = Errors.E930.format(name="Morphologizer", obj=type(get_examples))
            raise ValueError(err)
        for example in get_examples():
            for i, token in enumerate(example.reference):
                pos = token.pos_
                morph = token.morph_
                # create and add the combined morph+POS label
                morph_dict = Morphology.feats_to_dict(morph)
                if pos:
                    morph_dict[self.POS_FEAT] = pos
                norm_label = self.vocab.strings[self.vocab.morphology.add(morph_dict)]
                # add label->morph and label->POS mappings
                if norm_label not in self.cfg["labels_morph"]:
                    self.cfg["labels_morph"][norm_label] = morph
                    self.cfg["labels_pos"][norm_label] = POS_IDS[pos]
        self.set_output(len(self.labels))
        self.model.initialize()
        if sgd is None:
            sgd = self.create_optimizer()
        return sgd

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
                doc.c[j].morph = self.vocab.morphology.add(self.cfg["labels_morph"][morph])
                doc.c[j].pos = self.cfg["labels_pos"][morph]

            doc.is_morphed = True

    def get_loss(self, examples, scores):
        """Find the loss and gradient of loss for the batch of documents and
        their predicted scores.

        examples (Iterable[Examples]): The batch of examples.
        scores: Scores representing the model's predictions.
        RETUTNRS (Tuple[float, float]): The loss and the gradient.

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
                # doesn't, so if either is None, treat both as None here so that
                # truths doesn't end up with an unknown morph+POS combination
                if pos is None or morph is None:
                    pos = None
                    morph = None
                label_dict = Morphology.feats_to_dict(morph)
                if pos:
                    label_dict[self.POS_FEAT] = pos
                label = self.vocab.strings[self.vocab.morphology.add(label_dict)]
                eg_truths.append(label)
            truths.append(eg_truths)
        d_scores, loss = loss_func(scores, truths)
        if self.model.ops.xp.isnan(loss):
            raise ValueError("nan value when computing loss")
        return float(loss), d_scores

    def score(self, examples, **kwargs):
        """Score a batch of examples.

        examples (Iterable[Example]): The examples to score.
        RETURNS (Dict[str, Any]): The scores, produced by
            Scorer.score_token_attr for the attributes "pos" and "morph" and
            Scorer.score_token_attr_per_feat for the attribute "morph".

        DOCS: https://spacy.io/api/morphologizer#score
        """
        validate_examples(examples, "Morphologizer.score")
        results = {}
        results.update(Scorer.score_token_attr(examples, "pos", **kwargs))
        results.update(Scorer.score_token_attr(examples, "morph", **kwargs))
        results.update(Scorer.score_token_attr_per_feat(examples,
            "morph", **kwargs))
        return results

    def to_bytes(self, *, exclude=tuple()):
        """Serialize the pipe to a bytestring.

        exclude (Iterable[str]): String names of serialization fields to exclude.
        RETURNS (bytes): The serialized object.

        DOCS: https://spacy.io/api/morphologizer#to_bytes
        """
        serialize = {}
        serialize["model"] = self.model.to_bytes
        serialize["vocab"] = self.vocab.to_bytes
        serialize["cfg"] = lambda: srsly.json_dumps(self.cfg)
        return util.to_bytes(serialize, exclude)

    def from_bytes(self, bytes_data, *, exclude=tuple()):
        """Load the pipe from a bytestring.

        bytes_data (bytes): The serialized pipe.
        exclude (Iterable[str]): String names of serialization fields to exclude.
        RETURNS (Morphologizer): The loaded Morphologizer.

        DOCS: https://spacy.io/api/morphologizer#from_bytes
        """
        def load_model(b):
            try:
                self.model.from_bytes(b)
            except AttributeError:
                raise ValueError(Errors.E149) from None

        deserialize = {
            "vocab": lambda b: self.vocab.from_bytes(b),
            "cfg": lambda b: self.cfg.update(srsly.json_loads(b)),
            "model": lambda b: load_model(b),
        }
        util.from_bytes(bytes_data, deserialize, exclude)
        return self

    def to_disk(self, path, *, exclude=tuple()):
        """Serialize the pipe to disk.

        path (str / Path): Path to a directory.
        exclude (Iterable[str]): String names of serialization fields to exclude.

        DOCS: https://spacy.io/api/morphologizer#to_disk
        """
        serialize = {
            "vocab": lambda p: self.vocab.to_disk(p),
            "model": lambda p: p.open("wb").write(self.model.to_bytes()),
            "cfg": lambda p: srsly.write_json(p, self.cfg),
        }
        util.to_disk(path, serialize, exclude)

    def from_disk(self, path, *, exclude=tuple()):
        """Load the pipe from disk. Modifies the object in place and returns it.

        path (str / Path): Path to a directory.
        exclude (Iterable[str]): String names of serialization fields to exclude.
        RETURNS (Morphologizer): The modified Morphologizer object.

        DOCS: https://spacy.io/api/morphologizer#from_disk
        """
        def load_model(p):
            with p.open("rb") as file_:
                try:
                    self.model.from_bytes(file_.read())
                except AttributeError:
                    raise ValueError(Errors.E149) from None

        deserialize = {
            "vocab": lambda p: self.vocab.from_disk(p),
            "cfg": lambda p: self.cfg.update(deserialize_config(p)),
            "model": load_model,
        }
        util.from_disk(path, deserialize, exclude)
        return self
