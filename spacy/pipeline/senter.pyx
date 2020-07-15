# cython: infer_types=True, profile=True, binding=True
import srsly
from thinc.api import Model, SequenceCategoricalCrossentropy
from ..tokens.doc cimport Doc

from .pipe import load_config
from .tagger import Tagger
from ..language import Language
from ..util import link_vectors_to_models, load_config_from_str
from ..errors import Errors
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
dropout = null
"""
DEFAULT_SENTER_MODEL = load_config_from_str(default_model_config, create_objects=False)["model"]


@Language.factory(
    "senter",
    assigns=["token.is_sent_start"],
    default_config={"model": DEFAULT_SENTER_MODEL}
)
def make_senter(nlp: Language, name: str, model: Model):
    return SentenceRecognizer(nlp.vocab, model, name)


class SentenceRecognizer(Tagger):
    """Pipeline component for sentence segmentation.

    DOCS: https://spacy.io/api/sentencerecognizer
    """
    def __init__(self, vocab, model, name="senter"):
        self.vocab = vocab
        self.model = model
        self.name = name
        self._rehearsal_model = None
        self.cfg = {}

    @property
    def labels(self):
        # labels are numbered by index internally, so this matches GoldParse
        # and Example where the sentence-initial tag is 1 and other positions
        # are 0
        return tuple(["I", "S"])

    def set_annotations(self, docs, batch_tag_ids):
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
        labels = self.labels
        loss_func = SequenceCategoricalCrossentropy(names=labels, normalize=False)
        truths = []
        for eg in examples:
            eg_truth = []
            for x in eg.get_aligned("sent_start"):
                if x == None:
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

    def begin_training(self, get_examples=lambda: [], pipeline=None, sgd=None,
                       **kwargs):
        self.set_output(len(self.labels))
        self.model.initialize()
        link_vectors_to_models(self.vocab)
        if sgd is None:
            sgd = self.create_optimizer()
        return sgd

    def add_label(self, label, values=None):
        raise NotImplementedError

    def to_bytes(self, exclude=tuple()):
        serialize = {}
        serialize["model"] = self.model.to_bytes
        serialize["vocab"] = self.vocab.to_bytes
        serialize["cfg"] = lambda: srsly.json_dumps(self.cfg)
        return util.to_bytes(serialize, exclude)

    def from_bytes(self, bytes_data, exclude=tuple()):
        def load_model(b):
            try:
                self.model.from_bytes(b)
            except AttributeError:
                raise ValueError(Errors.E149)

        deserialize = {
            "vocab": lambda b: self.vocab.from_bytes(b),
            "cfg": lambda b: self.cfg.update(srsly.json_loads(b)),
            "model": lambda b: load_model(b),
        }
        util.from_bytes(bytes_data, deserialize, exclude)
        return self

    def to_disk(self, path, exclude=tuple()):
        serialize = {
            "vocab": lambda p: self.vocab.to_disk(p),
            "model": lambda p: p.open("wb").write(self.model.to_bytes()),
            "cfg": lambda p: srsly.write_json(p, self.cfg),
        }
        util.to_disk(path, serialize, exclude)

    def from_disk(self, path, exclude=tuple()):
        def load_model(p):
            with p.open("rb") as file_:
                try:
                    self.model.from_bytes(file_.read())
                except AttributeError:
                    raise ValueError(Errors.E149)

        deserialize = {
            "vocab": lambda p: self.vocab.from_disk(p),
            "cfg": lambda p: self.cfg.update(load_config(p)),
            "model": load_model,
        }
        util.from_disk(path, deserialize, exclude)
        return self
