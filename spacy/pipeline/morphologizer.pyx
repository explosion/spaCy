from __future__ import unicode_literals
from collections import OrderedDict, defaultdict

import numpy
cimport numpy as np

from thinc.api import chain
from thinc.neural.util import to_categorical, copy_array, get_array_module
from .. import util
from .pipes import Pipe
from ..language import component
from .._ml import Tok2Vec, build_morphologizer_model
from .._ml import link_vectors_to_models, zero_init, flatten
from .._ml import create_default_optimizer
from ..errors import Errors, TempErrors
from ..compat import basestring_
from ..tokens.doc cimport Doc
from ..vocab cimport Vocab
from ..morphology cimport Morphology


@component("morphologizer", assigns=["token.morph", "token.pos"])
class Morphologizer(Pipe):

    @classmethod
    def Model(cls, **cfg):
        if cfg.get('pretrained_dims') and not cfg.get('pretrained_vectors'):
            raise ValueError(TempErrors.T008)
        class_map = Morphology.create_class_map()
        return build_morphologizer_model(class_map.field_sizes, **cfg)

    def __init__(self, vocab, model=True, **cfg):
        self.vocab = vocab
        self.model = model
        self.cfg = OrderedDict(sorted(cfg.items()))
        self.cfg.setdefault('cnn_maxout_pieces', 2)
        self._class_map = self.vocab.morphology.create_class_map()

    @property
    def labels(self):
        return self.vocab.morphology.tag_names

    @property
    def tok2vec(self):
        if self.model in (None, True, False):
            return None
        else:
            return chain(self.model.tok2vec, flatten)

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

    def predict(self, docs):
        if not any(len(doc) for doc in docs):
            # Handle case where there are no tokens in any docs.
            n_labels = self.model.nO
            guesses = [self.model.ops.allocate((0, n_labels)) for doc in docs]
            tokvecs = self.model.ops.allocate((0, self.model.tok2vec.nO))
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
            doc_guesses = scores_to_guesses(doc_scores, self.model.softmax.out_sizes)
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

    def update(self, docs, golds, drop=0., sgd=None, losses=None):
        if losses is not None and self.name not in losses:
            losses[self.name] = 0.

        tag_scores, bp_tag_scores = self.model.begin_update(docs, drop=drop)
        loss, d_tag_scores = self.get_loss(docs, golds, tag_scores)
        bp_tag_scores(d_tag_scores, sgd=sgd)

        if losses is not None:
            losses[self.name] += loss

    def get_loss(self, docs, golds, scores):
        guesses = []
        for doc_scores in scores:
            guesses.append(scores_to_guesses(doc_scores, self.model.softmax.out_sizes))
        guesses = self.model.ops.xp.vstack(guesses)
        scores = self.model.ops.xp.vstack(scores)
        if not isinstance(scores, numpy.ndarray):
            scores = scores.get()
        if not isinstance(guesses, numpy.ndarray):
            guesses = guesses.get()
        cdef int idx = 0
        # Do this on CPU, as we can't vectorize easily.
        target = numpy.zeros(scores.shape, dtype='f')
        field_sizes = self.model.softmax.out_sizes
        for doc, gold in zip(docs, golds):
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
