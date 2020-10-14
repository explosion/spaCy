# cython: infer_types=True, profile=True, binding=True
from typing import Optional
import numpy
from thinc.api import CosineDistance, to_categorical, Model, Config
from thinc.api import set_dropout_rate

from ..tokens.doc cimport Doc

from .trainable_pipe import TrainablePipe
from .tagger import Tagger
from ..training import validate_examples
from ..language import Language
from ._parser_internals import nonproj
from ..attrs import POS, ID
from ..errors import Errors


default_model_config = """
[model]
@architectures = "spacy.MultiTask.v1"
maxout_pieces = 3
token_vector_width = 96

[model.tok2vec]
@architectures = "spacy.HashEmbedCNN.v1"
pretrained_vectors = null
width = 96
depth = 4
embed_size = 2000
window_size = 1
maxout_pieces = 2
subword_features = true
"""
DEFAULT_MT_MODEL = Config().from_str(default_model_config)["model"]


@Language.factory(
    "nn_labeller",
    default_config={"labels": None, "target": "dep_tag_offset", "model": DEFAULT_MT_MODEL}
)
def make_nn_labeller(nlp: Language, name: str, model: Model, labels: Optional[dict], target: str):
    return MultitaskObjective(nlp.vocab, model, name)


class MultitaskObjective(Tagger):
    """Experimental: Assist training of a parser or tagger, by training a
    side-objective.
    """

    def __init__(self, vocab, model, name="nn_labeller", *, labels, target):
        self.vocab = vocab
        self.model = model
        self.name = name
        if target == "dep":
            self.make_label = self.make_dep
        elif target == "tag":
            self.make_label = self.make_tag
        elif target == "ent":
            self.make_label = self.make_ent
        elif target == "dep_tag_offset":
            self.make_label = self.make_dep_tag_offset
        elif target == "ent_tag":
            self.make_label = self.make_ent_tag
        elif target == "sent_start":
            self.make_label = self.make_sent_start
        elif hasattr(target, "__call__"):
            self.make_label = target
        else:
            raise ValueError(Errors.E016)
        cfg = {"labels": labels or {}, "target": target}
        self.cfg = dict(cfg)

    @property
    def labels(self):
        return self.cfg.setdefault("labels", {})

    @labels.setter
    def labels(self, value):
        self.cfg["labels"] = value

    def set_annotations(self, docs, dep_ids):
        pass

    def initialize(self, get_examples, nlp=None):
        if not hasattr(get_examples, "__call__"):
            err = Errors.E930.format(name="MultitaskObjective", obj=type(get_examples))
            raise ValueError(err)
        for example in get_examples():
            for token in example.y:
                label = self.make_label(token)
                if label is not None and label not in self.labels:
                    self.labels[label] = len(self.labels)
        self.model.initialize()   # TODO: fix initialization by defining X and Y

    def predict(self, docs):
        tokvecs = self.model.get_ref("tok2vec")(docs)
        scores = self.model.get_ref("softmax")(tokvecs)
        return tokvecs, scores

    def get_loss(self, examples, scores):
        cdef int idx = 0
        correct = numpy.zeros((scores.shape[0],), dtype="i")
        guesses = scores.argmax(axis=1)
        docs = [eg.predicted for eg in examples]
        for i, eg in enumerate(examples):
            # Handles alignment for tokenization differences
            doc_annots = eg.get_aligned()  # TODO
            for j in range(len(eg.predicted)):
                tok_annots = {key: values[j] for key, values in tok_annots.items()}
                label = self.make_label(j, tok_annots)
                if label is None or label not in self.labels:
                    correct[idx] = guesses[idx]
                else:
                    correct[idx] = self.labels[label]
                idx += 1
        correct = self.model.ops.xp.array(correct, dtype="i")
        d_scores = scores - to_categorical(correct, n_classes=scores.shape[1])
        loss = (d_scores**2).sum()
        return float(loss), d_scores

    @staticmethod
    def make_dep(token):
        return token.dep_

    @staticmethod
    def make_tag(token):
        return token.tag_

    @staticmethod
    def make_ent(token):
        if token.ent_iob_ == "O":
            return "O"
        else:
            return token.ent_iob_ + "-" + token.ent_type_

    @staticmethod
    def make_dep_tag_offset(token):
        dep = token.dep_
        tag = token.tag_
        offset = token.head.i - token.i
        offset = min(offset, 2)
        offset = max(offset, -2)
        return f"{dep}-{tag}:{offset}"

    @staticmethod
    def make_ent_tag(token):
        if token.ent_iob_ == "O":
            ent = "O"
        else:
            ent = token.ent_iob_ + "-" + token.ent_type_
        tag = token.tag_
        return f"{tag}-{ent}"

    @staticmethod
    def make_sent_start(token):
        """A multi-task objective for representing sentence boundaries,
        using BILU scheme. (O is impossible)
        """
        if token.is_sent_start and token.is_sent_end:
            return "U-SENT"
        elif token.is_sent_start:
            return "B-SENT"
        else:
            return "I-SENT"


class ClozeMultitask(TrainablePipe):
    def __init__(self, vocab, model, **cfg):
        self.vocab = vocab
        self.model = model
        self.cfg = cfg
        self.distance = CosineDistance(ignore_zeros=True, normalize=False)  # TODO: in config

    def set_annotations(self, docs, dep_ids):
        pass

    def initialize(self, get_examples, nlp=None):
        self.model.initialize()  # TODO: fix initialization by defining X and Y
        X = self.model.ops.alloc((5, self.model.get_ref("tok2vec").get_dim("nO")))
        self.model.output_layer.initialize(X)

    def predict(self, docs):
        tokvecs = self.model.get_ref("tok2vec")(docs)
        vectors = self.model.get_ref("output_layer")(tokvecs)
        return tokvecs, vectors

    def get_loss(self, examples, vectors, prediction):
        validate_examples(examples, "ClozeMultitask.get_loss")
        # The simplest way to implement this would be to vstack the
        # token.vector values, but that's a bit inefficient, especially on GPU.
        # Instead we fetch the index into the vectors table for each of our tokens,
        # and look them up all at once. This prevents data copying.
        ids = self.model.ops.flatten([eg.predicted.to_array(ID).ravel() for eg in examples])
        target = vectors[ids]
        gradient = self.distance.get_grad(prediction, target)
        loss = self.distance.get_loss(prediction, target)
        return loss, gradient

    def update(self, examples, *, drop=0., set_annotations=False, sgd=None, losses=None):
        pass

    def rehearse(self, examples, drop=0., sgd=None, losses=None):
        if losses is not None and self.name not in losses:
            losses[self.name] = 0.
        set_dropout_rate(self.model, drop)
        validate_examples(examples, "ClozeMultitask.rehearse")
        docs = [eg.predicted for eg in examples]
        predictions, bp_predictions = self.model.begin_update()
        loss, d_predictions = self.get_loss(examples, self.vocab.vectors.data, predictions)
        bp_predictions(d_predictions)
        if sgd is not None:
            self.finish_update(sgd)
        if losses is not None:
            losses[self.name] += loss
        return losses

    def add_label(self, label):
        raise NotImplementedError
