# cython: infer_types=True, profile=True, binding=True
from itertools import islice

import srsly
from thinc.api import Model, SequenceCategoricalCrossentropy, Config

from ..tokens.doc cimport Doc

from .pipe import deserialize_config
from .tagger import Tagger
from ..language import Language
from ..errors import Errors
from ..scorer import Scorer
from ..training import validate_examples
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

    DOCS: https://nightly.spacy.io/api/sentencerecognizer
    """
    def __init__(self, vocab, model, name="senter"):
        """Initialize a sentence recognizer.

        vocab (Vocab): The shared vocabulary.
        model (thinc.api.Model): The Thinc Model powering the pipeline component.
        name (str): The component instance name, used to add entries to the
            losses during training.

        DOCS: https://nightly.spacy.io/api/sentencerecognizer#init
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

        DOCS: https://nightly.spacy.io/api/sentencerecognizer#set_annotations
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

    def update(self, examples, *, drop=0., sgd=None, losses=None, set_annotations=False):
        """Learn from a batch of documents and gold-standard information,
        updating the pipe's model. Delegates to predict and get_loss.

        examples (Iterable[Example]): A batch of Example objects.
        drop (float): The dropout rate.
        set_annotations (bool): Whether or not to update the Example objects
            with the predictions.
        sgd (thinc.api.Optimizer): The optimizer.
        losses (Dict[str, float]): Optional record of the loss during training.
            Updated using the component name as the key.
        RETURNS (Dict[str, float]): The updated losses dictionary.

        DOCS: https://nightly.spacy.io/api/tagger#update
        """
        if losses is None:
            losses = {}
        losses.setdefault(self.name, 0.0)
        validate_examples(examples, "Tagger.update")
        if not any(len(eg.predicted) if eg.predicted else 0 for eg in examples):
            # Handle cases where there are no tokens in any docs.
            return
        if not any(eg.reference.is_sentenced for eg in examples):
            # Handle cases where there are no tagged tokens in any docs.
            return
        set_dropout_rate(self.model, drop)
        tag_scores, bp_tag_scores = self.model.begin_update([eg.predicted for eg in examples])
        for sc in tag_scores:
            if self.model.ops.xp.isnan(sc.sum()):
                raise ValueError(Errors.E940)
        loss, d_tag_scores = self.get_loss(examples, tag_scores)
        bp_tag_scores(d_tag_scores)
        if sgd not in (None, False):
            self.model.finish_update(sgd)

        losses[self.name] += loss
        if set_annotations:
            docs = [eg.predicted for eg in examples]
            self.set_annotations(docs, self._scores2guesses(tag_scores))
        return losses



    def get_loss(self, examples, scores):
        """Find the loss and gradient of loss for the batch of documents and
        their predicted scores.

        examples (Iterable[Examples]): The batch of examples.
        scores: Scores representing the model's predictions.
        RETUTNRS (Tuple[float, float]): The loss and the gradient.

        DOCS: https://nightly.spacy.io/api/sentencerecognizer#get_loss
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
            raise ValueError("nan value when computing loss")
        return float(loss), d_scores

    def begin_training(self, get_examples, *, pipeline=None, sgd=None):
        """Initialize the pipe for training, using a representative set
        of data examples.

        get_examples (Callable[[], Iterable[Example]]): Function that
            returns a representative sample of gold-standard Example objects.
        pipeline (List[Tuple[str, Callable]]): Optional list of pipeline
            components that this component is part of. Corresponds to
            nlp.pipeline.
        sgd (thinc.api.Optimizer): Optional optimizer. Will be created with
            create_optimizer if it doesn't exist.
        RETURNS (thinc.api.Optimizer): The optimizer.

        DOCS: https://nightly.spacy.io/api/sentencerecognizer#begin_training
        """
        self._ensure_examples(get_examples)
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
        if sgd is None:
            sgd = self.create_optimizer()
        return sgd

    def add_label(self, label, values=None):
        raise NotImplementedError

    def score(self, examples, **kwargs):
        """Score a batch of examples.

        examples (Iterable[Example]): The examples to score.
        RETURNS (Dict[str, Any]): The scores, produced by Scorer.score_spans.
        DOCS: https://nightly.spacy.io/api/sentencerecognizer#score
        """
        validate_examples(examples, "SentenceRecognizer.score")
        results = Scorer.score_spans(examples, "sents", **kwargs)
        del results["sents_per_type"]
        return results

    def to_bytes(self, *, exclude=tuple()):
        """Serialize the pipe to a bytestring.

        exclude (Iterable[str]): String names of serialization fields to exclude.
        RETURNS (bytes): The serialized object.

        DOCS: https://nightly.spacy.io/api/sentencerecognizer#to_bytes
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

        DOCS: https://nightly.spacy.io/api/sentencerecognizer#from_bytes
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

        DOCS: https://nightly.spacy.io/api/sentencerecognizer#to_disk
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

        DOCS: https://nightly.spacy.io/api/sentencerecognizer#from_disk
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
