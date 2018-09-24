from __future__ import unicode_literals
from collections import OrderedDict, defaultdict
import cytoolz
import ujson

import numpy
cimport numpy as np
from .util import msgpack
from .util import msgpack_numpy

from thinc.api import chain
from thinc.neural.util import to_categorical, copy_array
from . import util
from .pipe import Pipe
from ._ml import Tok2Vec, build_tagger_model
from ._ml import link_vectors_to_models, zero_init, flatten
from ._ml import create_default_optimizer
from .errors import Errors, TempErrors
from .compat import json_dumps, basestring_
from .tokens.doc cimport Doc
from .vocab cimport Vocab
from .morphology cimport Morphology


class Morphologizer(Pipe):
    name = 'morphologizer'
    
    @classmethod
    def Model(cls, attr_nums, **cfg):
        if cfg.get('pretrained_dims') and not cfg.get('pretrained_vectors'):
            raise ValueError(TempErrors.T008)
        return build_morphologizer_model(attr_nums, **cfg)

    def __init__(self, vocab, model=True, **cfg):
        self.vocab = vocab
        self.model = model
        self.cfg = OrderedDict(sorted(cfg.items()))
        self.cfg.setdefault('cnn_maxout_pieces', 2)

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
        self.set_annotations([doc], tags, tensors=tokvecs)
        return doc

    def pipe(self, stream, batch_size=128, n_threads=-1):
        for docs in cytoolz.partition_all(batch_size, stream):
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
        guesses = []
        # Resolve multisoftmax into guesses
        for doc_scores in scores:
            guesses.append(scores_to_guesses(doc_scores, self.model.softmax.out_sizes))
        return guesses, tokvecs

    def set_annotations(self, docs, batch_feature_ids, tensors=None):
        if isinstance(docs, Doc):
            docs = [docs]
        cdef Doc doc
        cdef Vocab vocab = self.vocab
        for i, doc in enumerate(docs):
            doc_feat_ids = batch_feat_ids[i]
            if hasattr(doc_feat_ids, 'get'):
                doc_feat_ids = doc_feat_ids.get()
            # Convert the neuron indices into feature IDs.
            offset = self.vocab.morphology.first_feature
            for j, nr_feat in enumerate(self.model.softmax.out_sizes):
                doc_feat_ids[:, j] += offset
                offset += nr_feat
            # Now add the analysis, and set the hash.
            for j in range(doc_feat_ids.shape[0]):
                doc.c[j].morph = self.vocab.morphology.add(doc_feat_ids[j])

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
        guesses = self.model.ops.flatten(guesses)
        cdef int idx = 0
        target = numpy.zeros(scores.shape, dtype='f')
        for gold in golds:
            for features in gold.morphology:
                if features is None:
                    target[idx] = guesses[idx]
                else:
                    for feature in features:
                        column = feature_to_column(feature) # TODO
                        target[idx, column] = 1
                idx += 1
        target = self.model.ops.xp.array(target, dtype='f')
        d_scores = scores - target
        loss = (d_scores**2).sum()
        d_scores = self.model.ops.unflatten(d_scores, [len(d) for d in docs])
        return float(loss), d_scores

    def use_params(self, params):
        with self.model.use_params(params):
            yield
