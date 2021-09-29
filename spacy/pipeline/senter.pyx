# cython: infer_types=True, profile=True, binding=True
from itertools import islice
from typing import Optional, Callable

import srsly
from thinc.api import Model, SequenceCategoricalCrossentropy, Config

from ..tokens.doc cimport Doc

from .tagger import Tagger
from ..language import Language
from ..errors import Errors
from ..scorer import Scorer
from ..training import validate_examples, validate_get_examples
from ..util import registry
from .. import util

# See #9050
BACKWARD_OVERWRITE = False

default_model_config = """
[model]
@architectures = "spacy.Tagger.v1"

[model.tok2vec]
@architectures = "spacy.HashEmbedCNN.v2"
pretrained_vectors = null
width = 12
depth = 1
embed_size = 2000
window_size = 1
maxout_pieces = 2
subword_features = true
"""
DEFAULT_SENTER_MODEL = Config().from_str(default_model_config)["model"]


@Language.factory(
    "senter",
    assigns=["token.is_sent_start"],
    default_config={"model": DEFAULT_SENTER_MODEL, "overwrite": False, "scorer": {"@scorers": "spacy.senter_scorer.v1"}},
    default_score_weights={"sents_f": 1.0, "sents_p": 0.0, "sents_r": 0.0},
)
def make_senter(nlp: Language, name: str, model: Model, overwrite: bool, scorer: Optional[Callable]):
    return SentenceRecognizer(nlp.vocab, model, name, overwrite=overwrite, scorer=scorer)


def senter_score(examples, **kwargs):
    def has_sents(doc):
        return doc.has_annotation("SENT_START")

    results = Scorer.score_spans(examples, "sents", has_annotation=has_sents, **kwargs)
    del results["sents_per_type"]
    return results


@registry.scorers("spacy.senter_scorer.v1")
def make_senter_scorer():
    return senter_score


class SentenceRecognizer(Tagger):
    """Pipeline component for sentence segmentation.

    DOCS: https://spacy.io/api/sentencerecognizer
    """
    def __init__(
        self,
        vocab,
        model,
        name="senter",
        *,
        overwrite=BACKWARD_OVERWRITE,
        scorer=senter_score,
    ):
        """Initialize a sentence recognizer.

        vocab (Vocab): The shared vocabulary.
        model (thinc.api.Model): The Thinc Model powering the pipeline component.
        name (str): The component instance name, used to add entries to the
            losses during training.
        scorer (Optional[Callable]): The scoring method. Defaults to
            Scorer.score_spans for the attribute "sents".

        DOCS: https://spacy.io/api/sentencerecognizer#init
        """
        self.vocab = vocab
        self.model = model
        self.name = name
        self._rehearsal_model = None
        self.cfg = {"overwrite": overwrite}
        self.scorer = scorer

    @property
    def labels(self):
        """RETURNS (Tuple[str]): The labels."""
        # labels are numbered by index internally, so this matches GoldParse
        # and Example where the sentence-initial tag is 1 and other positions
        # are 0
        return tuple(["I", "S"])

    @property
    def label_data(self):
        return None

    def set_annotations(self, docs, batch_tag_ids):
        """Modify a batch of documents, using pre-computed scores.

        docs (Iterable[Doc]): The documents to modify.
        batch_tag_ids: The IDs to set, produced by SentenceRecognizer.predict.

        DOCS: https://spacy.io/api/sentencerecognizer#set_annotations
        """
        if isinstance(docs, Doc):
            docs = [docs]
        cdef Doc doc
        cdef bint overwrite = self.cfg["overwrite"]
        for i, doc in enumerate(docs):
            doc_tag_ids = batch_tag_ids[i]
            if hasattr(doc_tag_ids, "get"):
                doc_tag_ids = doc_tag_ids.get()
            for j, tag_id in enumerate(doc_tag_ids):
                if doc.c[j].sent_start == 0 or overwrite:
                    if tag_id == 1:
                        doc.c[j].sent_start = 1
                    else:
                        doc.c[j].sent_start = -1

    def get_loss(self, examples, scores):
        """Find the loss and gradient of loss for the batch of documents and
        their predicted scores.

        examples (Iterable[Examples]): The batch of examples.
        scores: Scores representing the model's predictions.
        RETURNS (Tuple[float, float]): The loss and the gradient.

        DOCS: https://spacy.io/api/sentencerecognizer#get_loss
        """
        validate_examples(examples, "SentenceRecognizer.get_loss")
        labels = self.labels
        loss_func = SequenceCategoricalCrossentropy(names=labels, normalize=False)
        truths = []
        for eg in examples:
            eg_truth = []
            for x in eg.get_aligned("SENT_START"):
                if x is None:
                    eg_truth.append(None)
                elif x == 1:
                    eg_truth.append(labels[1])
                else:
                    # anything other than 1: 0, -1, -1 as uint64
                    eg_truth.append(labels[0])
            truths.append(eg_truth)
        d_scores, loss = loss_func(scores, truths)
        if self.model.ops.xp.isnan(loss):
            raise ValueError(Errors.E910.format(name=self.name))
        return float(loss), d_scores

    def initialize(self, get_examples, *, nlp=None):
        """Initialize the pipe for training, using a representative set
        of data examples.

        get_examples (Callable[[], Iterable[Example]]): Function that
            returns a representative sample of gold-standard Example objects.
        nlp (Language): The current nlp object the component is part of.

        DOCS: https://spacy.io/api/sentencerecognizer#initialize
        """
        validate_get_examples(get_examples, "SentenceRecognizer.initialize")
        util.check_lexeme_norms(self.vocab, "senter")
        doc_sample = []
        label_sample = []
        assert self.labels, Errors.E924.format(name=self.name)
        for example in islice(get_examples(), 10):
            doc_sample.append(example.x)
            gold_tags = example.get_aligned("SENT_START")
            gold_array = [[1.0 if tag == gold_tag else 0.0 for tag in self.labels] for gold_tag in gold_tags]
            label_sample.append(self.model.ops.asarray(gold_array, dtype="float32"))
        assert len(doc_sample) > 0, Errors.E923.format(name=self.name)
        assert len(label_sample) > 0, Errors.E923.format(name=self.name)
        self.model.initialize(X=doc_sample, Y=label_sample)

    def add_label(self, label, values=None):
        raise NotImplementedError
