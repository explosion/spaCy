from __future__ import unicode_literals
from __future__ import division

from os import path
import os
import shutil
import json
import cython
import numpy.random

from thinc.features cimport Feature, count_feats


cdef int arg_max(const weight_t* scores, const int n_classes) nogil:
    cdef int i
    cdef int best = 0
    cdef weight_t mode = scores[0]
    for i in range(1, n_classes):
        if scores[i] > mode:
            mode = scores[i]
            best = i
    return best


cdef class Model:
    def __init__(self, n_classes, templates, model_loc=None):
        if model_loc is not None and path.isdir(model_loc):
            model_loc = path.join(model_loc, 'model')
        self.n_classes = n_classes
        self._extractor = Extractor(templates)
        self._model = LinearModel(n_classes, self._extractor.n_templ)
        self.model_loc = model_loc
        if self.model_loc and path.exists(self.model_loc):
            self._model.load(self.model_loc, freq_thresh=0)

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

    @cython.cdivision
    @cython.boundscheck(False)
    cdef int regularize(self, Feature* feats, int n, int a=3) except -1:
        cdef int i
        cdef long[:] zipfs = numpy.random.zipf(a, n)
        for i in range(n):
            feats[i].value *= 1 / zipfs[i]

    def end_training(self):
        self._model.end_training()
        self._model.dump(self.model_loc, freq_thresh=0)
