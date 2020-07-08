# cython: infer_types=True, profile=True
cimport numpy as np

import numpy
import srsly
from thinc.api import SequenceCategoricalCrossentropy

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
            for i, token in enumerate(example.reference):
                pos = token.pos_
                morph = token.morph
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
        loss_func = SequenceCategoricalCrossentropy(names=self.labels, normalize=False)
        truths = []
        for eg in examples:
            eg_truths = []
            pos_tags = eg.get_aligned("POS", as_string=True)
            morphs = eg.get_aligned("MORPH", as_string=True)
            for i in range(len(morphs)):
                pos = pos_tags[i]
                morph = morphs[i]
                feats = Morphology.feats_to_dict(morph)
                if pos:
                    feats["POS"] = pos
                if len(feats) > 0:
                    morph = self.vocab.strings[self.vocab.morphology.add(feats)]
                if morph == "":
                    morph = Morphology.EMPTY_MORPH
                eg_truths.append(morph)
            truths.append(eg_truths)
        d_scores, loss = loss_func(scores, truths)
        if self.model.ops.xp.isnan(loss):
            raise ValueError("nan value when computing loss")
        return float(loss), d_scores

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
            "cfg": lambda p: self.cfg.update(_load_cfg(p)),
            "model": load_model,
        }
        util.from_disk(path, deserialize, exclude)
        return self
