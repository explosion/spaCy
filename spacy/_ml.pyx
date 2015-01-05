from __future__ import unicode_literals
from __future__ import division

from os import path
import os
import shutil
import random
import json
import cython

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

    def end_training(self):
        self._model.end_training()
        self._model.dump(self.model_loc, freq_thresh=0)


cdef class HastyModel:
    def __init__(self, n_classes, hasty_templates, full_templates, model_dir):
        full_templates = tuple([t for t in full_templates if t not in hasty_templates])
        self.mem = Pool()
        self.n_classes = n_classes
        self._scores = <weight_t*>self.mem.alloc(self.n_classes, sizeof(weight_t))
        assert path.exists(model_dir)
        assert path.isdir(model_dir)
        self._hasty = Model(n_classes, hasty_templates, path.join(model_dir, 'hasty_model'))
        self._full = Model(n_classes, full_templates, path.join(model_dir, 'full_model'))
        self.hasty_cnt = 0
        self.full_cnt = 0

    cdef const weight_t* score(self, atom_t* context) except NULL:
        cdef int i
        hasty_scores = self._hasty.score(context)
        if will_use_hasty(hasty_scores, self._hasty.n_classes):
            self.hasty_cnt += 1
            return hasty_scores
        else:
            self.full_cnt += 1
            full_scores = self._full.score(context)
            for i in range(self.n_classes):
                self._scores[i] = full_scores[i] + hasty_scores[i]
            return self._scores

    cdef int update(self, atom_t* context, class_t guess, class_t gold, int cost) except -1:
        self._hasty.update(context, guess, gold, cost)
        self._full.update(context, guess, gold, cost)

    def end_training(self):
        self._hasty.end_training()
        self._full.end_training()


@cython.cdivision(True)
cdef bint will_use_hasty(const weight_t* scores, int n_classes) nogil:
    cdef:
        weight_t best_score, second_score
        int best, second

    if scores[0] >= scores[1]:
        best = 0
        best_score = scores[0]
        second = 1
        second_score = scores[1]
    else:
        best = 1
        best_score = scores[1]
        second = 0
        second_score = scores[0]
    cdef int i
    for i in range(2, n_classes):
        if scores[i] > best_score:
            second_score = best_score
            second = best
            best = i
            best_score = scores[i]
        elif scores[i] > second_score:
            second_score = scores[i]
            second = i
    return best_score > 0 and second_score < (best_score / 2)
