# cython: infer_types=True, profile=True, binding=True
import srsly
from thinc.api import Model, SequenceCategoricalCrossentropy, Config

from ..tokens.doc cimport Doc

from .pipe import deserialize_config
from .tagger import Tagger
from ..language import Language
from ..errors import Errors
from ..scorer import Scorer
from .. import util


default_model_config = """
[model]
@architectures = "spacy.Tagger.v1"

[model.tok2vec]
@architectures = "spacy.HashEmbedCNN.v1"
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
    default_config={"model": DEFAULT_SENTER_MODEL},
    scores=["sents_p", "sents_r", "sents_f"],
    default_score_weights={"sents_f": 1.0, "sents_p": 0.0, "sents_r": 0.0},
)
def make_senter(nlp: Language, name: str, model: Model):
    return SentenceRecognizer(nlp.vocab, model, name)


class SentenceRecognizer(Tagger):
    """Pipeline component for sentence segmentation.

    DOCS: https://spacy.io/api/sentencerecognizer
    """
    def __init__(self, vocab, model, name="senter"):
        """Initialize a sentence recognizer.

        vocab (Vocab): The shared vocabulary.
        model (thinc.api.Model): The Thinc Model powering the pipeline component.
        name (str): The component instance name, used to add entries to the
            losses during training.

        DOCS: https://spacy.io/api/sentencerecognizer#init
        """
        self.vocab = vocab
        self.model = model
        self.name = name
        self._rehearsal_model = None
        self.cfg = {}

    @property
    def labels(self):
        """RETURNS (Tuple[str]): The labels."""
        # labels are numbered by index internally, so this matches GoldParse
        # and Example where the sentence-initial tag is 1 and other positions
        # are 0
        return tuple(["I", "S"])

    def set_annotations(self, docs, batch_tag_ids):
        """Modify a batch of documents, using pre-computed scores.

        docs (Iterable[Doc]): The documents to modify.
        batch_tag_ids: The IDs to set, produced by SentenceRecognizer.predict.

        DOCS: https://spacy.io/api/sentencerecognizer#set_annotations
        """
        if isinstance(docs, Doc):
            docs = [docs]
        cdef Doc doc
        for i, doc in enumerate(docs):
            doc_tag_ids = batch_tag_ids[i]
            if hasattr(doc_tag_ids, "get"):
                doc_tag_ids = doc_tag_ids.get()
            for j, tag_id in enumerate(doc_tag_ids):
                # Don't clobber existing sentence boundaries
                if doc.c[j].sent_start == 0:
                    if tag_id == 1:
                        doc.c[j].sent_start = 1
                    else:
                        doc.c[j].sent_start = -1

    def get_loss(self, examples, scores):
        """Find the loss and gradient of loss for the batch of documents and
        their predicted scores.

        examples (Iterable[Examples]): The batch of examples.
        scores: Scores representing the model's predictions.
        RETUTNRS (Tuple[float, float]): The loss and the gradient.

        DOCS: https://spacy.io/api/sentencerecognizer#get_loss
        """
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
            raise ValueError("nan value when computing loss")
        return float(loss), d_scores

    def begin_training(self, get_examples=lambda: [], *, pipeline=None, sgd=None):
        """Initialize the pipe for training, using data examples if available.

        get_examples (Callable[[], Iterable[Example]]): Optional function that
            returns gold-standard Example objects.
        pipeline (List[Tuple[str, Callable]]): Optional list of pipeline
            components that this component is part of. Corresponds to
            nlp.pipeline.
        sgd (thinc.api.Optimizer): Optional optimizer. Will be created with
            create_optimizer if it doesn't exist.
        RETURNS (thinc.api.Optimizer): The optimizer.

        DOCS: https://spacy.io/api/sentencerecognizer#begin_training
        """
        self.set_output(len(self.labels))
        self.model.initialize()
        if sgd is None:
            sgd = self.create_optimizer()
        return sgd

    def add_label(self, label, values=None):
        raise NotImplementedError

    def score(self, examples, **kwargs):
        """Score a batch of examples.

        examples (Iterable[Example]): The examples to score.
        RETURNS (Dict[str, Any]): The scores, produced by Scorer.score_spans.
        DOCS: https://spacy.io/api/sentencerecognizer#score
        """
        results = Scorer.score_spans(examples, "sents", **kwargs)
        del results["sents_per_type"]
        return results

    def to_bytes(self, *, exclude=tuple()):
        """Serialize the pipe to a bytestring.

        exclude (Iterable[str]): String names of serialization fields to exclude.
        RETURNS (bytes): The serialized object.

        DOCS: https://spacy.io/api/sentencerecognizer#to_bytes
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
        RETURNS (Tagger): The loaded SentenceRecognizer.

        DOCS: https://spacy.io/api/sentencerecognizer#from_bytes
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

        DOCS: https://spacy.io/api/sentencerecognizer#to_disk
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
        RETURNS (Tagger): The modified SentenceRecognizer object.

        DOCS: https://spacy.io/api/sentencerecognizer#from_disk
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
