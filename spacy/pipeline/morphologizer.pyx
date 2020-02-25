from collections import defaultdict

import numpy
cimport numpy as np

from thinc.api import chain, list2array, to_categorical, get_array_module
from thinc.util import copy_array

from .. import util
from .pipes import Pipe
from ..language import component
from ..util import link_vectors_to_models, create_default_optimizer
from ..errors import Errors, TempErrors
from ..tokens.doc cimport Doc
from ..vocab cimport Vocab
from ..morphology cimport Morphology


@component("morphologizer", assigns=["token.morph", "token.pos"])
class Morphologizer(Pipe):

    def __init__(self, vocab, **cfg):
        self.vocab = vocab
        self.model = True
        self.cfg = dict(sorted(cfg.items()))
        self._class_map = self.vocab.morphology.create_class_map()  # Morphology.create_class_map() ?

    @property
    def labels(self):
        return self.vocab.morphology.tag_names

    def default_model_config(self):
        from ..ml.models import default_morphologizer_config   #  avoid circular imports
        return default_morphologizer_config()

    def define_output_dim(self):
        return len(self.labels)

    @property
    def tok2vec(self):
        if self.model in (None, True, False):
            return None
        else:
            return chain(self.model.get_ref("tok2vec"), list2array())

    def __call__(self, doc):
        features, tokvecs = self.predict([doc])
        self.set_annotations([doc], features, tensors=tokvecs)
        return doc

    def pipe(self, stream, batch_size=128, n_threads=-1):
        for docs in util.minibatch(stream, size=batch_size):
            docs = list(docs)
            features, tokvecs = self.predict(docs)
            self.set_annotations(docs, features, tensors=tokvecs)
            yield from docs

    def begin_training(self, get_examples=lambda: [], pipeline=None, sgd=None,
                       **kwargs):
        if self.model is True:
            self.model = self.Model()
        self.model.initialize()
        if sgd is None:
            sgd = self.create_optimizer()
        return sgd

    def predict(self, docs):
        if not any(len(doc) for doc in docs):
            # Handle case where there are no tokens in any docs.
            n_labels = self.model.get_dim("nO")
            guesses = [self.model.ops.alloc((0, n_labels)) for doc in docs]
            tokvecs = self.model.ops.alloc((0, self.model.get_ref("tok2vec").get_dim("nO")))
            return guesses, tokvecs
        tokvecs = self.model.tok2vec(docs)
        scores = self.model.softmax(tokvecs)
        return scores, tokvecs

    def set_annotations(self, docs, batch_scores, tensors=None):
        if isinstance(docs, Doc):
            docs = [docs]
        cdef Doc doc
        cdef Vocab vocab = self.vocab
        offsets = [self._class_map.get_field_offset(field)
                   for field in self._class_map.fields]
        for i, doc in enumerate(docs):
            doc_scores = batch_scores[i]
            doc_guesses = scores_to_guesses(doc_scores, self.model.get_ref("softmax").attrs["nOs"])
            # Convert the neuron indices into feature IDs.
            doc_feat_ids = numpy.zeros((len(doc), len(self._class_map.fields)), dtype='i')
            for j in range(len(doc)):
                for k, offset in enumerate(offsets):
                    if doc_guesses[j, k] == 0:
                        doc_feat_ids[j, k] = 0
                    else:
                        doc_feat_ids[j, k] = offset + doc_guesses[j, k]
                # Get the set of feature names.
                feats = {self._class_map.col2info[f][2] for f in doc_feat_ids[j]}
                if "NIL" in feats:
                    feats.remove("NIL")
                # Now add the analysis, and set the hash.
                doc.c[j].morph = self.vocab.morphology.add(feats)
                if doc[j].morph.pos != 0:
                    doc.c[j].pos = doc[j].morph.pos

    def update(self, examples, drop=0., sgd=None, losses=None):
        if losses is not None and self.name not in losses:
            losses[self.name] = 0.

        docs = [self._get_doc(ex) for ex in examples]
        tag_scores, bp_tag_scores = self.model.begin_update(docs, drop=drop)
        loss, d_tag_scores = self.get_loss(examples, tag_scores)
        bp_tag_scores(d_tag_scores, sgd=sgd)

        if losses is not None:
            losses[self.name] += loss

    def get_loss(self, examples, scores):
        guesses = []
        for doc_scores in scores:
            guesses.append(scores_to_guesses(doc_scores, self.model.get_ref("softmax").attrs["nOs"]))
        guesses = self.model.ops.xp.vstack(guesses)
        scores = self.model.ops.xp.vstack(scores)
        if not isinstance(scores, numpy.ndarray):
            scores = scores.get()
        if not isinstance(guesses, numpy.ndarray):
            guesses = guesses.get()
        cdef int idx = 0
        # Do this on CPU, as we can't vectorize easily.
        target = numpy.zeros(scores.shape, dtype='f')
        field_sizes = self.model.get_ref("softmax").attrs["nOs"]
        for example in examples:
            doc = example.doc
            gold = example.gold
            for t, features in enumerate(gold.morphology):
                if features is None:
                    target[idx] = scores[idx]
                else:
                    gold_fields = {}
                    for feature in features:
                        field = self._class_map.feat2field[feature]
                        gold_fields[field] = self._class_map.feat2offset[feature]
                    for field in self._class_map.fields:
                        field_id = self._class_map.field2id[field]
                        col_offset = self._class_map.field2col[field]
                        if field_id in gold_fields:
                            target[idx, col_offset + gold_fields[field_id]] = 1.
                        else:
                            target[idx, col_offset] = 1.
                    #print(doc[t])
                    #for col, info in enumerate(self._class_map.col2info):
                    #    print(col, info, scores[idx, col], target[idx, col])
                idx += 1
        target = self.model.ops.asarray(target, dtype='f')
        scores = self.model.ops.asarray(scores, dtype='f')
        d_scores = scores - target
        loss = (d_scores**2).sum()
        docs = [self._get_doc(ex) for ex in examples]
        d_scores = self.model.ops.unflatten(d_scores, [len(d) for d in docs])
        return float(loss), d_scores

    def use_params(self, params):
        with self.model.use_params(params):
            yield

def scores_to_guesses(scores, out_sizes):
    xp = get_array_module(scores)
    guesses = xp.zeros((scores.shape[0], len(out_sizes)), dtype='i')
    offset = 0
    for i, size in enumerate(out_sizes):
        slice_ = scores[:, offset : offset + size]
        col_guesses = slice_.argmax(axis=1)
        guesses[:, i] = col_guesses
        offset += size
    return guesses
