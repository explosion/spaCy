# cython: infer_types=True, profile=True
cimport numpy as np

import numpy
import srsly
from thinc.api import to_categorical

from ..tokens.doc cimport Doc
from ..vocab cimport Vocab
from ..morphology cimport Morphology
from ..parts_of_speech import IDS as POS_IDS
from ..symbols import POS

from .. import util
from ..language import component
from ..util import link_vectors_to_models, create_default_optimizer
from ..errors import Errors, TempErrors
from .pipes import Tagger, _load_cfg
from .. import util
from .defaults import default_morphologizer


@component("morphologizer", assigns=["token.morph", "token.pos"], default_model=default_morphologizer)
class Morphologizer(Tagger):

    def __init__(self, vocab, model, **cfg):
        self.vocab = vocab
        self.model = model
        self._rehearsal_model = None
        self.cfg = dict(sorted(cfg.items()))
        self.cfg.setdefault("labels", {})
        self.cfg.setdefault("morph_pos", {})

    @property
    def labels(self):
        return tuple(self.cfg["labels"].keys())

    def add_label(self, label):
        if not isinstance(label, str):
            raise ValueError(Errors.E187)
        if label in self.labels:
            return 0
        morph = Morphology.feats_to_dict(label)
        norm_morph_pos = self.vocab.strings[self.vocab.morphology.add(morph)]
        pos = morph.get("POS", "")
        if norm_morph_pos not in self.cfg["labels"]:
            self.cfg["labels"][norm_morph_pos] = norm_morph_pos
            self.cfg["morph_pos"][norm_morph_pos] = POS_IDS[pos]
        return 1

    def begin_training(self, get_examples=lambda: [], pipeline=None, sgd=None,
                       **kwargs):
        for example in get_examples():
            for i, morph in enumerate(example.token_annotation.morphs):
                pos = example.token_annotation.get_pos(i)
                morph = Morphology.feats_to_dict(morph)
                norm_morph = self.vocab.strings[self.vocab.morphology.add(morph)]
                if pos:
                    morph["POS"] = pos
                norm_morph_pos = self.vocab.strings[self.vocab.morphology.add(morph)]
                if norm_morph_pos not in self.cfg["labels"]:
                    self.cfg["labels"][norm_morph_pos] = norm_morph
                    self.cfg["morph_pos"][norm_morph_pos] = POS_IDS[pos]
        self.set_output(len(self.labels))
        self.model.initialize()
        link_vectors_to_models(self.vocab)
        if sgd is None:
            sgd = self.create_optimizer()
        return sgd

    def set_annotations(self, docs, batch_tag_ids):
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
                doc.c[j].morph = self.vocab.morphology.add(self.cfg["labels"][morph])
                doc.c[j].pos = self.cfg["morph_pos"][morph]

            doc.is_morphed = True

    def get_loss(self, examples, scores):
        scores = self.model.ops.flatten(scores)
        tag_index = {tag: i for i, tag in enumerate(self.labels)}
        cdef int idx = 0
        correct = numpy.zeros((scores.shape[0],), dtype="i")
        guesses = scores.argmax(axis=1)
        known_labels = numpy.ones((scores.shape[0], 1), dtype="f")
        for ex in examples:
            gold = ex.gold
            for i in range(len(gold.morphs)):
                pos = gold.pos[i] if i < len(gold.pos) else ""
                morph = gold.morphs[i]
                feats = Morphology.feats_to_dict(morph)
                if pos:
                    feats["POS"] = pos
                if len(feats) > 0:
                    morph = self.vocab.strings[self.vocab.morphology.add(feats)]
                if morph == "":
                    morph = Morphology.EMPTY_MORPH
                if morph is None:
                    correct[idx] = guesses[idx]
                elif morph in tag_index:
                    correct[idx] = tag_index[morph]
                else:
                    correct[idx] = 0
                    known_labels[idx] = 0.
                idx += 1
        correct = self.model.ops.xp.array(correct, dtype="i")
        d_scores = scores - to_categorical(correct, n_classes=scores.shape[1])
        d_scores *= self.model.ops.asarray(known_labels)
        loss = (d_scores**2).sum()
        docs = [ex.doc for ex in examples]
        d_scores = self.model.ops.unflatten(d_scores, [len(d) for d in docs])
        return float(loss), d_scores

    def to_bytes(self, exclude=tuple(), **kwargs):
        serialize = {}
        serialize["model"] = self.model.to_bytes
        serialize["vocab"] = self.vocab.to_bytes
        serialize["cfg"] = lambda: srsly.json_dumps(self.cfg)
        exclude = util.get_serialization_exclude(serialize, exclude, kwargs)
        return util.to_bytes(serialize, exclude)

    def from_bytes(self, bytes_data, exclude=tuple(), **kwargs):
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
        exclude = util.get_serialization_exclude(deserialize, exclude, kwargs)
        util.from_bytes(bytes_data, deserialize, exclude)
        return self

    def to_disk(self, path, exclude=tuple(), **kwargs):
        serialize = {
            "vocab": lambda p: self.vocab.to_disk(p),
            "model": lambda p: p.open("wb").write(self.model.to_bytes()),
            "cfg": lambda p: srsly.write_json(p, self.cfg),
        }
        exclude = util.get_serialization_exclude(serialize, exclude, kwargs)
        util.to_disk(path, serialize, exclude)

    def from_disk(self, path, exclude=tuple(), **kwargs):
        def load_model(p):
            with p.open("rb") as file_:
                try:
                    self.model.from_bytes(file_.read())
                except AttributeError:
                    raise ValueError(Errors.E149)

        deserialize = {
            "vocab": lambda p: self.vocab.from_disk(p),
            "cfg": lambda p: self.cfg.update(_load_cfg(p)),
            "model": load_model,
        }
        exclude = util.get_serialization_exclude(deserialize, exclude, kwargs)
        util.from_disk(path, deserialize, exclude)
        return self
