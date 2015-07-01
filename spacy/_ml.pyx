# cython: profile=True
from __future__ import unicode_literals
from __future__ import division

from os import path
import os
import shutil
import json
import cython
import numpy.random

from thinc.features cimport Feature, count_feats
from thinc.api cimport Example


cdef int arg_max(const weight_t* scores, const int n_classes) nogil:
    cdef int i
    cdef int best = 0
    cdef weight_t mode = scores[0]
    for i in range(1, n_classes):
        if scores[i] > mode:
            mode = scores[i]
            best = i
    return best


cdef int arg_max_if_true(const weight_t* scores, const int* is_valid,
                         const int n_classes) nogil:
    cdef int i
    cdef int best = 0
    cdef weight_t mode = -900000
    for i in range(n_classes):
        if is_valid[i] and scores[i] > mode:
            mode = scores[i]
            best = i
    return best


cdef int arg_max_if_zero(const weight_t* scores, const int* costs,
                         const int n_classes) nogil:
    cdef int i
    cdef int best = 0
    cdef weight_t mode = -900000
    for i in range(n_classes):
        if costs[i] == 0 and scores[i] > mode:
            mode = scores[i]
            best = i
    return best


cdef class Model:
    def __init__(self, n_classes, templates, model_loc=None):
        if model_loc is not None and path.isdir(model_loc):
            model_loc = path.join(model_loc, 'model')
        self.n_classes = n_classes
        self._extractor = Extractor(templates)
        self.n_feats = self._extractor.n_templ
        self._model = LinearModel(n_classes, self._extractor.n_templ)
        self.model_loc = model_loc
        if self.model_loc and path.exists(self.model_loc):
            self._model.load(self.model_loc, freq_thresh=0)

    def predict(self, Example eg):
        self.set_scores(eg.c.scores, eg.c.atoms)
        eg.c.guess = arg_max_if_true(eg.c.scores, eg.c.is_valid, self.n_classes)

    def train(self, Example eg):
        self.predict(eg)
        eg.c.best = arg_max_if_zero(eg.c.scores, eg.c.costs, self.n_classes)
        eg.c.cost = eg.c.costs[eg.c.guess]
        self.update(eg.c.atoms, eg.c.guess, eg.c.best, eg.c.cost)

    cdef const weight_t* score(self, atom_t* context) except NULL:
        cdef int n_feats
        feats = self._extractor.get_feats(context, &n_feats)
        return self._model.get_scores(feats, n_feats)

    cdef int set_scores(self, weight_t* scores, atom_t* context) except -1:
        cdef int n_feats
        feats = self._extractor.get_feats(context, &n_feats)
        self._model.set_scores(scores, feats, n_feats)

    cdef int update(self, atom_t* context, class_t guess, class_t gold, int cost) except -1:
        cdef int n_feats
        if cost == 0:
            self._model.update({})
        else:
            feats = self._extractor.get_feats(context, &n_feats)
            counts = {gold: {}, guess: {}}
            count_feats(counts[gold], feats, n_feats, cost)
            count_feats(counts[guess], feats, n_feats, -cost)
            self._model.update(counts)

    def end_training(self):
        self._model.end_training()
        self._model.dump(self.model_loc, freq_thresh=0)
